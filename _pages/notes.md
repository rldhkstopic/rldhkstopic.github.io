---
layout: page
title: "Research Notes"
permalink: /notes/
---

{% for post in site.posts %}
  {% if post.categories contains "Research" %}
    - [{{ post.title }}]({{ post.url }})
  {% endif %}
{% endfor %}
