#

## Introduction

The main problem with LLMs I found is their inability to make use of discoveries/preferences across tasks (chats). A lot of people talk about the usefulness of **in-context learning**. This, in my view, represents the working memory or **the short-term memory**. It is extremely useful for most tasks as it allows the LLM to *learn* from examples that have been put into its context, apart from the actual task at hand. As great as **ICL** might be, it is missing a few crucial elements:

- Ability to store/retrieve knowledge across tasks.
- Ability to share and collect knowledge from other agents.
- etc.

To fix this, I propose a very pragmatic and practical approach that should, in theory, be applicable to any LLM (actually, more powerful LLMs should benefit even more than basic ones). It involves a way of constructing a *general knowledge domain* that can be accessed/edited by multiple agents and serves as something resembeling *culture* in human affairs; as well as one *special knowledge domain*, unique to each agent - something like a *identitiy* in humans.

As Andrej Karpathy said in a recent interview, we can see LLM pre-training as a way of creating a "base-case" or "prepackaging intelligence". This then needs to be complemented with useful information. Although this approach is not considering any conflicts that might arise from pre-training vs. in-context data, it is a **Model-Agnostic** approach that doesn't care about the actual base-model. Future extensions might take the above issue into account, although this task is more likely to fall onto the LLM engineers to implement.

## An ignorant review of human history

>*Agriculture as the enabler of civilization, and writing as the multiplier of knowledge.*

Most of the inspiration is taken from human civilization. The astonishing fact is that the humans we know today emerged almost 300,000 years ago, whereas the first "civilization" came into being only about 7,500 years ago (the Sumerian Civilization in Mesopotamia). I find this to be the case due to the invention of writing coupled with agriculture. Here, it is important to note that the time from the invention of agriculture to the city of Uruk spanned around 5,500 years.

Agriculture allowed humans to stay in one place and led them to start building villages and later cities, eliminating the need to continue a nomadic lifestyle. This allowed generations to actually build upon and improve things. The subsequent emergence of writing helped in transmitting knowledge across generations without relying on a few individuals (elders) to remember and pass down everything.

## Sleep

The world we live in is extremely complex. While awake, we ignore much of the infomation we receive. Think of walking to work while intensely thinking about something. When you arrive at work, you remember almost nothing from that walk. Even during the walk you sometimes miss a car approaching. This is something we partially solved with LLMs by the *attention* mechanism. Certain tokens get larger weights if they are important for the context of the next token.

However, if we just relied on short-term memory (i.e., LLM context windows) and the attention mechanism, we would run into the bounds of effective context windows of those LLMs. In other words, we are missing a *regularization* process that *distills* the *learned*. Sleep is when humans do this. We never memorize everything. There is a hidden mechanism of how *information importance* is being determined and applied to distilling the data we absorb. 

I imagine such a concept to be applicable to even today's LLMs in order to improve their **intelligence** across tasks and inside similar environments. This is precisely what we need in order to make agents useful. They need to **grow** with the environments they are in. 

To sum up, with the combination of the attention mechanism in the context window of an LLM, combined with their own long-term memory (**identity**) as well as the shared long-term memory (**culture**), regularized through a process of information distillation (**sleep**), I hope to create useful agents that can aid in complex environments across tasks while constantly specializing themselves to thrive in those environments.

## The Three-Layer Model

I propose here a simple layered model to achieve all the things promised above. The model consists of three core components:

- Culture (shared distilled knowledge)
- Identitiy (personal distilled knowledge)
- Awareness (short-term memory; working memory)

### Awareness
The **awareness** is basically the context of the LLM. It is the direct working memor, or the *prompt*. This is directly fed into the LLM and from it we expect direct answers form the LLM (MCP calls, Coder calls or textual answers). The main issue at hand here is **how to populate the awareness** to produce the best results. This is, as we will see below, achieved through **loading** relevant pieces of information from the **Identitiy** as well the **Culture**. 

### Identity

### Culture

