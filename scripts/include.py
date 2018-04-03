import os
import sys
import time
import itertools
from jinja2 import Template

dir = 'output/'
selfdir = 'scripts/'

size = 2 ** 15
chunkbits = 12
chunksize = 2 ** chunkbits

data = [0] * size
version = None
compiletime = time.strftime('%H:%M %d/%m-%y')

if len(sys.argv) < 2:
    raise ValueError('File not provided')

with open(dir + sys.argv[1], 'r')as f:
    for line in f:
        if not version and line.startswith('#version'):
            version = line.partition('=')[2].strip()
        line = line.partition('#')[0]
        if not line:
            continue

        address, value = map(int, line.split())
        data[address] = value

headertemplate = """
#pragma once

extern const char mdataversion[{{version|length}}];
extern const char mdatacompiletime[{{compiletime|length}}];

unsigned long readmdata(unsigned int address);
"""

cpptemplate = """
#pragma once

#include "mdata.h"
#include "avr\pgmspace.h"

const char mdataversion[{{version|length}}] = "{{version}}";
extern const char mdatacompiletime[{{compiletime|length}}] = "{{compiletime}}";

{% for chunk in chunks %}

const unsigned long mdata{{loop.index0}}[{{chunksize}}] PROGMEM = {
{% for row in chunk|batch(20) %}{% for column in row %}{{column}}UL, {% endfor %}
{%endfor%}
};
{% endfor %}


unsigned long readmdata(unsigned int address)
{
  unsigned int chunk=address>>{{chunkbits}};
  unsigned int index=address&{{chunksize-1}};

  unsigned long ptr=0;

  switch(chunk)
  {
    {% for chunk in chunks %}
    case {{loop.index0}}:
    ptr = pgm_get_far_address(mdata{{loop.index0}}[0]);
    break;
    {% endfor %}

    default:
    return 0;
  }
  ptr += index * sizeof(mdata0[0]);
  return pgm_read_dword_far(ptr);
}
"""


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]


with open(dir + 'mdata.h', 'w+') as w:
    w.write(Template(headertemplate).render(version=version, compiletime=compiletime))

with open(dir + 'mdata.cpp', 'w+') as w:
    w.write(
        Template(cpptemplate).render(version=version, compiletime=compiletime, chunkbits=chunkbits, chunksize=chunksize,
                                     chunks=[x for x in chunks(data, chunksize)]))
