# pygrl
Programmatically interact with Tinder using [pynder](https://github.com/charliewolf/pynder) (which in turn uses the [Tinder API](https://gist.github.com/rtt/10403467)).

Connection to Facebook is done using shamelessly copied [Weboob](https://github.com/laurentb/weboob) code. 

To get started:
```python
from pygrl import connect

session = connect(email, passwd)  # Connect to Facebook, then to Tinder, and return a pynder Session object
```
