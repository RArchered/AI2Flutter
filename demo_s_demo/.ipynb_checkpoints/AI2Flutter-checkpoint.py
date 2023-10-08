import logging
import time

import numpy as np
#import matplotlib.pyplot as plt
import tensorflow as tf

# 位置编码矩阵，输入length为序列长度，depth为单个token向量的长度
def positional_encoding(length, depth):
  depth = depth/2

  positions = np.arange(length)[:, np.newaxis]     # (seq, 1)
  depths = np.arange(depth)[np.newaxis, :]/depth   # (1, depth)
  
  angle_rates = 1 / (10000**depths)         # (1, depth)
  angle_rads = positions * angle_rates      # (pos, depth)

  pos_encoding = np.concatenate(
      [np.sin(angle_rads), np.cos(angle_rads)],
      axis=-1) 

  return tf.cast(pos_encoding, dtype=tf.float32)

class PositionalEmbedding(tf.keras.layers.Layer):
  """位置编码层
  
  用于将输入序列中的向量维数映射到模型维数，并增加位置编码
  !!!注意，位置编码长度已经固定在512，序列长度不能超过512，否则位置编码不够

  Attributes:
    d_model: 模型维数
    embedding: 全连接层，用于把节点的维数转换为模型维数
    pos_encoding: 位置矩阵
  """
  
  def __init__(self, vocab, d_model):
    super().__init__()
    self.d_model = d_model
    # 使用全链接层对输入向量（已经编码）映射到模型的维度
    self.embedding = tf.keras.layers.Embedding(vocab, d_model) 
    self.pos_encoding = positional_encoding(length=2048, depth=d_model)

  def compute_mask(self, *args, **kwargs):
    return self.embedding.compute_mask(*args, **kwargs)

  def call(self, x):
    length = tf.shape(x)[1]
    # print(tf.shape(x))
    # 降维
    x = self.embedding(x)
    # 降低模型的量级，尽量使得位置编码生效
    x *= tf.math.sqrt(tf.cast(self.d_model, tf.float32))
    x = x + self.pos_encoding[tf.newaxis, :length, :]
    return x

class BaseAttention(tf.keras.layers.Layer):
  """基础注意力层

  Transformer模型中一个通用注意力块
  
  Attributes:
    mha: 多头注意力层mha，接受头数和向量维数两个参数
    layernorm: 层标准化，将向量标准化
    add: 残差add层
  """

  def __init__(self, **kwargs):
    super().__init__()
    self.mha = tf.keras.layers.MultiHeadAttention(**kwargs)
    self.layernorm = tf.keras.layers.LayerNormalization()
    self.add = tf.keras.layers.Add()

class CrossAttention(BaseAttention):
  """交叉注意力层
  
  输入x查询向量，会在上下文key、value中查询
  """

  def call(self, x, context):
    attn_output, attn_scores = self.mha(
        query=x,
        key=context,
        value=context,
        return_attention_scores=True)

    # Cache the attention scores for plotting later.
    self.last_attn_scores = attn_scores
    # 残差连接
    x = self.add([x, attn_output])
    # 层标准化化
    x = self.layernorm(x)

    return x

class GlobalSelfAttention(BaseAttention):
  """自注意力层

  查询向量、键向量、值向量为同一个
  """

  def call(self, x):
    attn_output = self.mha(
        query=x,
        value=x,
        key=x)
    x = self.add([x, attn_output])
    x = self.layernorm(x)
    return x

# 带因果掩码的自注意力层
class CausalSelfAttention(BaseAttention):
  """带因果掩码的自注意力层

  在解码模块输入时，为了并发训练，使用teacher forcing时不能让前面的向量知道之后的信息，增加掩码
  """

  def call(self, x):
    attn_output = self.mha(
        query=x,
        value=x,
        key=x,
        use_causal_mask = True)
    x = self.add([x, attn_output])
    x = self.layernorm(x)
    return x

class FeedForward(tf.keras.layers.Layer):
  """前馈层

  用于在多头注意力层之后做变换

  Attributes:
    seq: 两层全连接，一层dropout
    layernorm: 层标准化，将向量标准化
    add: 残差add层
  """

  def __init__(self, d_model, dff, dropout_rate=0.1):
    super().__init__()
    self.seq = tf.keras.Sequential([
      tf.keras.layers.Dense(dff, activation='relu'),
      tf.keras.layers.Dense(d_model),
      tf.keras.layers.Dropout(dropout_rate)
    ])
    self.add = tf.keras.layers.Add()
    self.layer_norm = tf.keras.layers.LayerNormalization()

  def call(self, x):
    x = self.add([x, self.seq(x)])
    x = self.layer_norm(x) 
    return x

class EncoderLayer(tf.keras.layers.Layer):
  """编码器层

  Attributes:
    self_attention: 自注意力层
    ffn: 前馈层
  """
  
  def __init__(self,*, d_model, num_heads, dff, dropout_rate):
    """
    Args:
      d_model: 模型维数
      num_heads: 头数
      dff: 前馈层中间的维数
      dropout_rate: 丢弃率
    """
    super().__init__()
    self.self_attention = GlobalSelfAttention(
        num_heads=num_heads,
        key_dim=d_model,
        dropout=dropout_rate)

    self.ffn = FeedForward(d_model, dff)

  def call(self, x):
    x = self.self_attention(x)
    x = self.ffn(x)
    return x

class Encoder(tf.keras.layers.Layer):
  def __init__(self, *, num_layers, d_model, num_heads,
               dff, input_vocab, dropout_rate=0.1):
    """Transformer整个编码器模块

    Args:
      num_layers: 编码器层的层数
      d_model: 模型维数
      num_heads: 头数
      dff: 前馈层中间维数
      node_dim: 节点向量的维数
      dropout_rate: 丢弃率
    """
    
    super().__init__()
    self.d_model = d_model
    self.num_layers = num_layers
    self.pos_embedding = PositionalEmbedding(
        vocab=input_vocab, d_model=d_model)
    self.enc_layers = [
        EncoderLayer(d_model=d_model,
                     num_heads=num_heads,
                     dff=dff,
                     dropout_rate=dropout_rate)
        for _ in range(num_layers)]
    self.dropout = tf.keras.layers.Dropout(dropout_rate)

  def call(self, x):
    # `x` is node shape: (batch, seq_len, node_dim)
    x = self.pos_embedding(x)  # Shape `(batch_size, seq_len, d_model)`.

    # Add dropout.
    x = self.dropout(x)

    for i in range(self.num_layers):
      x = self.enc_layers[i](x)

    return x  # Shape `(batch_size, seq_len, d_model)`.

class DecoderLayer(tf.keras.layers.Layer):
  def __init__(self,
               *,
               d_model,
               num_heads,
               dff,
               dropout_rate=0.1):
    """
    Args:
      d_model: 模型维数
      num_heads: 头数
      dff: 前馈层中间的维数
      dropout_rate: 丢弃率
    """        
    
    super(DecoderLayer, self).__init__()
    self.causal_self_attention = CausalSelfAttention(
        num_heads=num_heads,
        key_dim=d_model,
        dropout=dropout_rate)

    self.cross_attention = CrossAttention(
        num_heads=num_heads,
        key_dim=d_model,
        dropout=dropout_rate)

    self.ffn = FeedForward(d_model, dff)

  def call(self, x, context):
    x = self.causal_self_attention(x=x)
    x = self.cross_attention(x=x, context=context)

    # Cache the last attention scores for plotting later
    self.last_attn_scores = self.cross_attention.last_attn_scores

    x = self.ffn(x)  # Shape `(batch_size, seq_len, d_model)`.
    return x

class Decoder(tf.keras.layers.Layer):
  def __init__(self, *, num_layers, d_model, num_heads, dff, output_vocab,
               dropout_rate=0.1):
    """Transformer整个解码器模块

    Args:
      num_layers: 编码器层的层数
      d_model: 模型维数
      num_heads: 头数
      dff: 前馈层中间维数
      node_dim: 节点向量的维数
      dropout_rate: 丢弃率
    """
    super(Decoder, self).__init__()
    self.d_model = d_model
    self.num_layers = num_layers

    self.pos_embedding = PositionalEmbedding(vocab=output_vocab,
                                             d_model=d_model)
    self.dropout = tf.keras.layers.Dropout(dropout_rate)
    self.dec_layers = [
        DecoderLayer(d_model=d_model, num_heads=num_heads,
                     dff=dff, dropout_rate=dropout_rate)
        for _ in range(num_layers)]

    self.last_attn_scores = None

  def call(self, x, context):
    # `x` is token-IDs shape (batch, target_seq_len)
    x = self.pos_embedding(x)  # (batch_size, target_seq_len, d_model)

    x = self.dropout(x)

    for i in range(self.num_layers):
      x  = self.dec_layers[i](x, context)

    self.last_attn_scores = self.dec_layers[-1].last_attn_scores

    # The shape of x is (batch_size, target_seq_len, d_model).
    return x

# transformer最终结构
# output_size为最终输出的向量的维数，在文本翻译过程中是词向量的长度，但在这里是flutter组件节点向量
class Transformer(tf.keras.Model):
  def __init__(self, *, num_layers, d_model, num_heads, dff,
               input_vocab, output_vocab, dropout_rate=0.1):
    super().__init__()
    self.encoder = Encoder(num_layers=num_layers, d_model=d_model,
                           num_heads=num_heads, dff=dff,
                           input_vocab=input_vocab,
                           dropout_rate=dropout_rate)

    self.decoder = Decoder(num_layers=num_layers, d_model=d_model,
                           num_heads=num_heads, dff=dff,
                           output_vocab=output_vocab,
                           dropout_rate=dropout_rate)

    self.final_layer = tf.keras.layers.Dense(output_vocab)

  def call(self, inputs):
    # To use a Keras model with `.fit` you must pass all your inputs in the
    # first argument.
    context, x  = inputs

    context = self.encoder(context)  # (batch_size, context_len, d_model)
    x = self.decoder(x, context)  # (batch_size, target_len, d_model)

    # Final linear layer output.
    logits = self.final_layer(x)  # (batch_size, target_len, target_vocab_size)

    try:
      # Drop the keras mask, so it doesn't scale the losses/metrics.
      # b/250038731
      del logits._keras_mask
    except AttributeError:
      pass

    # Return the final output and the attention weights.
    return logits

class CustomSchedule(tf.keras.optimizers.schedules.LearningRateSchedule):
  """自定义学习率
  """

  def __init__(self, d_model, warmup_steps=4000):
    super().__init__()

    self.d_model = d_model
    self.d_model = tf.cast(self.d_model, tf.float32)

    self.warmup_steps = warmup_steps
    
  def get_config(self):
    config = {
    'd_model': self.d_model,
    'warmup_steps': self.warmup_steps,
    }
    return config

  def __call__(self, step):
    step = tf.cast(step, dtype=tf.float32)
    arg1 = tf.math.rsqrt(step)
    arg2 = step * (self.warmup_steps ** -1.5)

    return tf.math.rsqrt(self.d_model) * tf.math.minimum(arg1, arg2)
    
        
