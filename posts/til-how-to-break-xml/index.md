---
date: "2022-11-02"
layout: post
title: "TIL: How to break RSS feeds"
categories: [blogging, code, writing, TIL]
---

> Note: this is the first post under a new tag called TIL or "today I learned". These are shorter format posts that lower the barrier to blogging and capture a mini piece of learning. The idea for TILs has been inspired by Simon Willison's own [TIL posts](https://til.simonwillison.net/).

It's really useful to have an RSS feed associated with a blog so that people can automatically pick up new posts. A lot of blogging technology (including Quarto and Jekyll) automatically creates these feeds at a URL called `<website name>/index.xml`, or similar, relative to the root of your website.

![The RSS feed icon (Image: Wikipedia)](https://upload.wikimedia.org/wikipedia/en/thumb/4/43/Feed-icon.svg/256px-Feed-icon.svg.png)

But I kept finding a problem with generating these feeds: either they did not generate at all or they were corrupted and unreadable.

I use a lot of latex in my blog posts. You can do this inline using dollar signs or as a display equation using double dollar signs in a separate paragraph. So

```text
$$
{\displaystyle F_{ij}=G\cdot {\frac {M_{i}M_{j}}{D_{ij}}}.}
$$
```

becomes

$$
{\displaystyle F_{ij}=G\cdot {\frac {M_{i}M_{j}}{D_{ij}}}.}
$$

So far so good. But, when you're putting latex in a code block---for example, when you're demonstrating how to add an equation to a chart in **matplotlib** in code---the string with latex in can crash the automatic blog RSS feed generator.

An example of the kind of string in a blog post that causes the problem is:

````text
```python
ax.set_xlabel(r"$e^\frac{-x^2}{2}$")
```
````

except with the `"` characters replaced with `'` because, ironically, I can't write this string without breaking the feed again.

The solution---as you can probably guess by now---is to use `"` instead of `'` for literal strings with latex in them in code blocks.

And, if you're digesting this via an RSS feed, you'll know it's worked!
