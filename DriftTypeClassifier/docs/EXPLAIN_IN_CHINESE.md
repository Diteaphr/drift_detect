# 用中文解释：Episodic、Encoder、FAN、时间步数

## 1. Episodic training 用中文解释

**「Episodic training = 每个 batch 是一个新的随机 episode（不同的 support/query）。模型学的是：同类靠近、异类远离的嵌入，这样任意 episode 里用最近原型都能分对。」**

拆开说：

- **Episode（一集/一个任务）**  
  每次不是「拿一整批 32 个样本一起训练」，而是：  
  - 先**随机抽 3 个类**（比如 sudden、gradual、incremental）；  
  - 每个类抽 **5 个 support**、**15 个 query**；  
  - 用这 15 个 support 算出 **3 个类中心（prototype）**；  
  - 再用「**谁离哪个类中心最近**」去预测 45 个 query 的类别。  
  这样的一整套，叫 **一个 episode**。

- **每个 batch = 一个新的随机 episode**  
  下一个 batch 再随机抽 3 个类、新的 support、新的 query，所以**每次的「题目」都不一样**（不同的 support/query 组合）。  
  训练时就是：不断换这种「小任务」，让模型在这种任务上降低预测误差。

- **模型在学什么**  
  不学「一个固定的线性分类器」，而是学一个 **嵌入（embedding）**：  
  - **同类**的样本在嵌入空间里**靠得近**；  
  - **不同类**的样本在嵌入空间里**离得远**。  
  这样，随便给你一个新的 episode（新的 support/query），你只要：  
  - 用 support 算 3 个类中心；  
  - 对每个 query 看它离哪个中心最近，就预测哪一类。  
  所以叫：**「same class → close, different class → far」**，这样 **nearest-prototype（最近原型）** 在任意 episode 里都能 work。

一句话：**Episodic 训练 = 用不断变化的「小任务」（不同 support/query）训练，让模型学会一个「同类近、异类远」的嵌入空间，这样用最近原型就能分类。**  

---

## 2. 什么是 Encoder（编码器）？

**Encoder** = 把你看到的**原始输入**变成**一个向量（嵌入）**的那一部分网络。  
输入是什么、输出是什么，由你设计；在这里：

- **输入：** 一条 stream 对应的 **14 维 gap 向量**（一个样本）。
- **输出：** 一个 **固定长度的向量**（比如 32 维或 64 维），叫做 **embedding（嵌入）**。

所以：  
**Encoder = 从「14 维 gap」到「一个向量」的映射。**  
后面的「怎么用这个向量来分类」可以不一样：  
- 有的模型是 **Encoder + 一个线性层**（standard）；  
- 有的是 **Encoder + 按最近类中心分类**（episodic / ProtoNet）。  
但**把 14 维变成向量的那一块**，都叫 Encoder。

---

## 3. 什么是 FAN？

**FAN = Full Attention Network**，就是你代码里用的那种 **基于注意力的编码器**。

- 它把输入（14 个数，可以看成「14 个时间步」）先通过一个**线性层**映射到高维；  
- 加上**位置编码**；  
- 再通过几层 **Transformer 的自注意力 + 前馈网络**；  
- 最后做**全局平均**，得到一个向量。  

所以：  
**FAN = 用 Transformer（自注意力）做成的 Encoder**，专门把「一段序列」（在这里是 14 维 gap）编码成一个向量。  
「FAN light」就是把层数、头数、维度改小一点的 FAN，还是同一类结构，只是更轻量。

---

## 4. 一条 stream 里有多少个时间步（timestamp）？

在**原始数据**里，一条 stream 是一个**时间序列**：

- 默认配置里 **`stream_length: 2000`**；  
- 所以一条 stream 有 **2000 个时间步**（t = 0, 1, …, 1999）。  
- 每个时间步上有：  
  - 特征向量（例如 10 维），和  
  - 一个类别标签。

也就是说：**一条 stream = 2000 个 timestamp。**  

但要注意：  
- 这 2000 步是**还没做 gap 之前**的「原始流」。  
- 做完在线分类、得到 error 序列，再在 **alert 时间**前后取窗口、划 15 段、算 gap，得到的是 **14 个数**。  
- 所以：  
  - **Stream 本身**：2000 个时间步；  
  - **送给模型的输入**：每个 stream 只对应**一个 14 维向量**（14 个 gap），不再保留 2000 步。

总结：  
- **Encoder** = 把 14 维 gap 变成向量的网络；  
- **FAN** = 用 Transformer 做的那种 Encoder；  
- **Episodic** = 用「不断换 support/query 的小任务」训练，学「同类近、异类远」的嵌入；  
- **一条 stream 的时间步数** = 2000（原始流），但模型只看到每个 stream 的 **1 个 14 维向量**。
