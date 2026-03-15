---
title: "Transformer 아키텍처 심층 분석"
description: "Attention 메커니즘부터 최신 효율적 Transformer 변형까지, 핵심 구조와 수학적 기반을 분석한다."
author: "kiwanPark"
date: 2026-03-12
doc_category: "연구 논문"
tags: ["Transformer", "Attention", "LLM", "딥러닝", "NLP"]
version: "1.0"
github_path: "_docs/transformer-architecture-analysis.md"
revisions:
  - version: "1.0"
    date: "2026-03-12"
    summary: "초기 문서 작성"
    changes:
      - type: added
        description: "Transformer 전체 구조 분석"
      - type: added
        description: "효율적 Attention 변형 정리"
---

## 개요

2017년 Vaswani 등이 발표한 "Attention Is All You Need" 논문은 자연어 처리(NLP) 분야의 패러다임을 근본적으로 변화시켰다. 기존 RNN/LSTM 기반 시퀀스 모델의 순차적 처리 한계를 Self-Attention 메커니즘으로 극복함으로써, 병렬 처리 효율성과 장거리 의존성 모델링 능력을 동시에 확보했다.

본 문서에서는 Transformer의 핵심 구성 요소를 수학적으로 분석하고, 최신 효율적 변형 아키텍처들을 비교 검토한다.

## Self-Attention 메커니즘

### Scaled Dot-Product Attention

Transformer의 핵심인 Scaled Dot-Product Attention은 Query($\mathbf{Q}$), Key($\mathbf{K}$), Value($\mathbf{V}$) 세 행렬의 연산으로 정의된다:

$$\text{Attention}(\mathbf{Q}, \mathbf{K}, \mathbf{V}) = \text{softmax}\left(\frac{\mathbf{Q}\mathbf{K}^T}{\sqrt{d_k}}\right)\mathbf{V}$$

여기서 $d_k$는 Key 벡터의 차원이며, $\sqrt{d_k}$로 나누는 스케일링은 내적 값이 커질 때 softmax 함수의 기울기가 극도로 작아지는 문제를 방지한다.

입력 시퀀스 $\mathbf{X} \in \mathbb{R}^{n \times d_{model}}$에서 Q, K, V는 학습 가능한 가중치 행렬을 통해 생성된다:

$$\mathbf{Q} = \mathbf{X}\mathbf{W}^Q, \quad \mathbf{K} = \mathbf{X}\mathbf{W}^K, \quad \mathbf{V} = \mathbf{X}\mathbf{W}^V$$

### Multi-Head Attention

단일 Attention 대신 $h$개의 독립적인 Attention Head를 병렬로 수행하여, 서로 다른 표현 부분공간(subspace)의 정보를 동시에 학습한다:

$$\text{MultiHead}(\mathbf{Q}, \mathbf{K}, \mathbf{V}) = \text{Concat}(\text{head}_1, \ldots, \text{head}_h)\mathbf{W}^O$$

각 head는:

$$\text{head}_i = \text{Attention}(\mathbf{Q}\mathbf{W}_i^Q, \mathbf{K}\mathbf{W}_i^K, \mathbf{V}\mathbf{W}_i^V)$$

GPT-3의 경우 $d_{model} = 12288$, $h = 96$이므로 각 head의 차원은 $d_k = d_v = 128$이다.

### 계산 복잡도

Self-Attention의 계산 복잡도는 $O(n^2 \cdot d)$이다. 시퀀스 길이 $n$에 대해 이차적으로 증가하며, 이는 긴 시퀀스 처리의 주요 병목이다:

| 연산 | 복잡도 | 메모리 |
|------|--------|--------|
| $\mathbf{QK}^T$ 계산 | $O(n^2 d)$ | $O(n^2)$ |
| Softmax | $O(n^2)$ | $O(n^2)$ |
| Attention × V | $O(n^2 d)$ | $O(nd)$ |
| **총합** | **$O(n^2 d)$** | **$O(n^2 + nd)$** |

## Transformer 블록 구조

### Encoder 블록

```
Input → LayerNorm → Multi-Head Attention → Residual Add
      → LayerNorm → Feed-Forward Network → Residual Add → Output
```

각 서브레이어에 잔차 연결(residual connection)과 레이어 정규화(Layer Normalization)가 적용된다:

$$\text{output} = \text{LayerNorm}(\mathbf{x} + \text{Sublayer}(\mathbf{x}))$$

### Feed-Forward Network

Position-wise FFN은 두 개의 선형 변환 사이에 활성화 함수를 적용한다:

$$\text{FFN}(\mathbf{x}) = \text{GELU}(\mathbf{x}\mathbf{W}_1 + \mathbf{b}_1)\mathbf{W}_2 + \mathbf{b}_2$$

일반적으로 내부 차원 $d_{ff} = 4 \times d_{model}$로 설정한다. GPT-3에서는 $d_{ff} = 49152$이다.

### 위치 인코딩(Positional Encoding)

Transformer는 순서 정보를 내재하지 않으므로, 위치 인코딩을 통해 시퀀스 내 위치 정보를 주입한다.

**사인/코사인 인코딩** (원본 Transformer):

$$PE_{(pos, 2i)} = \sin\left(\frac{pos}{10000^{2i/d_{model}}}\right)$$
$$PE_{(pos, 2i+1)} = \cos\left(\frac{pos}{10000^{2i/d_{model}}}\right)$$

**RoPE (Rotary Position Embedding)**:

최근 LLM에서 널리 사용되는 RoPE는 회전 행렬을 이용하여 상대적 위치 정보를 인코딩한다:

$$f(\mathbf{q}, m) = \mathbf{R}_m \mathbf{q}$$

여기서 $\mathbf{R}_m$은 위치 $m$에 해당하는 블록 대각 회전 행렬이다. 이 방식은 내적 기반 attention에서 자연스럽게 상대적 위치 정보를 반영한다.

## 효율적 Transformer 변형

시퀀스 길이에 대한 이차 복잡도 문제를 해결하기 위한 다양한 접근법이 제안되었다.

### Sparse Attention

**BigBird** 및 **Longformer**는 전체 attention 행렬 대신 희소 attention 패턴을 사용한다:

- **Local attention**: 인접한 $w$개 토큰에만 attention
- **Global attention**: 특정 토큰(예: [CLS])이 전체 시퀀스에 attention
- **Random attention**: 무작위로 선택된 토큰 쌍에 attention

복잡도: $O(n \cdot w)$ (로컬 윈도우 크기 $w$에 비례)

### Linear Attention

**Linear Transformer**는 softmax 함수를 커널 함수 $\phi$로 대체하여 계산 순서를 변경한다:

$$\text{LinearAttn}(\mathbf{Q}, \mathbf{K}, \mathbf{V}) = \frac{\phi(\mathbf{Q})(\phi(\mathbf{K})^T \mathbf{V})}{\phi(\mathbf{Q})\phi(\mathbf{K})^T \mathbf{1}}$$

연관 법칙을 이용하면 $\phi(\mathbf{K})^T \mathbf{V}$를 먼저 계산할 수 있으므로 복잡도가 $O(n \cdot d^2)$로 감소한다.

### Flash Attention

**Flash Attention**은 알고리즘 자체의 복잡도를 줄이지 않지만, GPU 메모리 계층을 최적화하여 실질적인 속도 향상을 달성한다:

- HBM(고대역 메모리)과 SRAM(온칩 메모리) 간 데이터 이동 최소화
- Tiling과 recomputation 기법으로 $O(n)$ 메모리 사용
- 표준 attention 대비 2-4배 속도 향상

```python
# Flash Attention 의사코드 (간략화)
def flash_attention(Q, K, V, block_size):
    N = Q.shape[0]
    output = zeros_like(Q)

    for i in range(0, N, block_size):
        q_block = Q[i:i+block_size]
        row_max = full(-inf, block_size)
        row_sum = zeros(block_size)
        acc = zeros(block_size, V.shape[1])

        for j in range(0, N, block_size):
            k_block = K[j:j+block_size]
            v_block = V[j:j+block_size]

            scores = q_block @ k_block.T / sqrt(d_k)
            block_max = scores.max(dim=-1)

            new_max = maximum(row_max, block_max)
            exp_old = exp(row_max - new_max)
            exp_new = exp(scores - new_max.unsqueeze(-1))

            acc = acc * exp_old.unsqueeze(-1) + exp_new @ v_block
            row_sum = row_sum * exp_old + exp_new.sum(dim=-1)
            row_max = new_max

        output[i:i+block_size] = acc / row_sum.unsqueeze(-1)

    return output
```

### 변형 아키텍처 비교

| 모델 | 시간 복잡도 | 공간 복잡도 | 장점 | 단점 |
|------|------------|------------|------|------|
| Standard | $O(n^2 d)$ | $O(n^2)$ | 높은 표현력 | 긴 시퀀스 불가 |
| Sparse (Longformer) | $O(n \cdot w)$ | $O(n \cdot w)$ | 긴 시퀀스 처리 | 패턴 설계 필요 |
| Linear | $O(n \cdot d^2)$ | $O(n \cdot d)$ | 선형 복잡도 | 성능 저하 가능 |
| Flash Attention | $O(n^2 d)$ | $O(n)$ | 실질 속도↑ | 알고리즘 복잡 |
| Mamba (SSM) | $O(n \cdot d)$ | $O(n \cdot d)$ | 선형, 인과적 | 양방향 불가 |

## KV Cache 최적화

자기회귀(autoregressive) 생성 시, 이전 토큰의 Key/Value를 캐싱하여 중복 계산을 제거한다.

### 메모리 사용량

모델 파라미터 $P$, 시퀀스 길이 $n$, 배치 크기 $B$에 대한 KV Cache 메모리:

$$M_{KV} = 2 \times L \times n \times B \times d_{model} \times \text{sizeof(dtype)}$$

GPT-3 (175B) 기준, 시퀀스 길이 2048, 배치 크기 1, FP16:

$$M_{KV} = 2 \times 96 \times 2048 \times 1 \times 12288 \times 2 = 9.66 \text{ GB}$$

### GQA (Grouped Query Attention)

**LLaMA 2**에서 도입한 GQA는 Key/Value head 수를 줄여 KV Cache 메모리를 절감한다:

- MHA: Q head = K head = V head = $h$
- MQA: Q head = $h$, K head = V head = 1
- GQA: Q head = $h$, K head = V head = $g$ ($1 < g < h$)

LLaMA 2 70B의 경우 $h = 64$, $g = 8$로 설정하여 KV Cache를 8배 절감했다.

## 결론

Transformer 아키텍처는 Self-Attention의 강력한 표현력을 기반으로 NLP를 넘어 비전, 음성, 과학 계산 등 다양한 분야에 확산되었다. 그러나 이차 복잡도와 메모리 요구량은 여전히 핵심 과제이며, Flash Attention, Linear Attention, SSM 기반 모델(Mamba) 등의 효율적 변형이 이를 해결하기 위해 활발히 연구되고 있다.

향후 연구 방향으로는 하드웨어-소프트웨어 공동 최적화, 긴 컨텍스트 처리(100K+ 토큰), 그리고 Attention과 SSM의 하이브리드 아키텍처가 유망하다.

## References

[^1]: [Attention Is All You Need (Vaswani et al., 2017)](https://arxiv.org/abs/1706.03762) - Transformer 원본 논문.
[^2]: [FlashAttention: Fast and Memory-Efficient Exact Attention](https://arxiv.org/abs/2205.14135) - Flash Attention 논문.
[^3]: [RoFormer: Enhanced Transformer with Rotary Position Embedding](https://arxiv.org/abs/2104.09864) - RoPE 논문.
[^4]: [LLaMA 2: Open Foundation and Fine-Tuned Chat Models](https://arxiv.org/abs/2307.09288) - LLaMA 2 및 GQA.
[^5]: [Mamba: Linear-Time Sequence Modeling with Selective State Spaces](https://arxiv.org/abs/2312.00752) - Mamba SSM 모델.
