```meta
title: Debug Page
```

# Test Title Here

## Test Primary Heading

This is a block of test.
<img src="/projects/website/thumb.png" class="float_right">
* It contains a test
* _With several items_
* `And some code`
* [__**_And some nested modifiers_**__](https://example.com)
  * Woah, that was pretty cool!
  * Oh, good, nesting works as well.
    * I had almost forgotten about that
      * How far can I go?
      * ~~I probably won't go any farther than this in an actual page.~~ said a past me

You can also create multi-item lists:
1. Bread
2. Eggs [^1]
3. Butter
   1. Margarine also acceptable
      1. I can't believe it's butter!
      2. Another thing
   2. Idk something else I forgot [^2]
   * Does making hybrid lists work?
     * Woah

```python
import numpy as np


class Funkinator(np.ndarray):
    def __init__(self, bananas: int):
        self.wolf = []
        self.wolf.append(bananas)
    
    # no, pycharm, you do not need to critique my embedded/example code block
    def some_code(self, data: np.ndarray, control: bool = False):
        # Numpy my beloved
        if not control:
            return sum(data) / data.std()
```

```markdown
# Test Title
* **Bolded List item**
  * `Some code`
```

```nginx
user  nginx;
worker_processes  auto;

error_log  /var/log/nginx/error.log notice;
pid        /var/run/nginx.pid;


events {
    worker_connections  4096;
}


http {
	server {  # test.ntos.tech
		listen 443 ssl http2;
		server_name test.ntos.tech;
		log_not_found off;

		location /static/ {
			root /hosts/test.ntos.tech/;
			try_files $uri $uri.html $uri/ =404;
		}
		
		location / {
			proxy_pass "http://webhost:43680";
			proxy_set_header Host $http_host;
			proxy_set_header X-Real-IP $remote_addr;
			proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
			proxy_set_header X-Forwarded-Proto $scheme;
			proxy_redirect off;
		}

		include nginx.ssl.conf;
	}


	server {  # photos.ntos.tech
		listen 443 ssl http2;
		server_name photos.ntos.tech;
		client_max_body_size 500M;

		location / {
			proxy_pass "http://photoprism:2342/";
			proxy_http_version 1.1;
			proxy_set_header Host $host;
			proxy_set_header Upgrade $http_upgrade;
			proxy_set_header Connection "upgrade";
			proxy_set_header X-Forwarded-For $remote_addr;
			proxy_redirect off;
			proxy_buffering off;
		}
	}
}
```
[^1]: sorry vegans 

# Not The Title

## Second Primary Heading

### Topic introduction

Good news everyone! We are going to learn some math today

#### A super long heading title that also contains a math section to test with

$$
\hat{\vec{z}} = \hat{\vec{x}} \cross \hat{\vec{y}}
$$

As you can see, the reference vector $\hat{\vec{z}}$ can be obtained via the cross product of X and Y. well, that is,
unless I haven't enabled the math plugin. Oops...

[^2]: I might remember later 

