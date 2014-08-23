# This file is free software and can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version. See the LICENSE file for more details.
#
# A simple Makefile to generate the virtualenv for different Python versions.
# Use it as you base template and adjust accordingly.

# The default directory name of the virtual environment.
VIRTUALDIR = env

clean:
	@! test -d $(VIRTUALDIR) || rm -rf $(VIRTUALDIR)
	@rm -rf setuptools*.zip
	@find . -name "*.py[cod]" -delete

test:
	nosetests -v

26: _python2.6
27: _python2.7
32: _python3.2
33: _python3.3
34: _python3.4

# Some legacy distro still contain Python 2.6.
_python2.6:
	@type python2.6 2> /dev/null || exit 1
	@test -f $(VIRTUALDIR)/bin/python2.6 || virtualenv -p python2.6 $(VIRTUALDIR)
	@make _requirements

_python2.7:
	@type python2.7 2> /dev/null || exit 1
	@test -f $(VIRTUALDIR)/bin/python2.7 || virtualenv -p python2.7 $(VIRTUALDIR)
	@make _requirements

# If setuptools or distribute is not available, get-pip.py will install it for
# you. See https://pip.pypa.io/en/latest/installing.html
_python3.2:
	@type python3.2 2> /dev/null || exit 1
	@test -f $(VIRTUALDIR)/bin/python3.2 || virtualenv -p python3.2 $(VIRTUALDIR)
	@test -f $(VIRTUALDIR)/bin/pip3.2 || { . $(VIRTUALDIR)/bin/activate; wget https://bootstrap.pypa.io/get-pip.py -O - | python; }
	@make _requirements

_python3.3:
	@type python3.3 2> /dev/null || exit 1
	@test -f $(VIRTUALDIR)/bin/python3.3 || pyvenv-3.3 $(VIRTUALDIR)
	@test -f $(VIRTUALDIR)/bin/pip3.3 || { . $(VIRTUALDIR)/bin/activate; wget https://bootstrap.pypa.io/get-pip.py -O - | python; }
	@make _requirements

# Python 3.4's virtualenv in Ubuntu is broken.  See
# https://news.ycombinator.com/item?id=7604177
_python3.4:
	@type python3.4 2> /dev/null || exit 1
	@test -f $(VIRTUALDIR)/bin/python3.4 || pyvenv-3.4 --without-pip $(VIRTUALDIR)
	@test -f $(VIRTUALDIR)/bin/pip3.4 || { . $(VIRTUALDIR)/bin/activate; wget https://bootstrap.pypa.io/get-pip.py -O - | python; }
	@make _requirements

_requirements:
	@ . $(VIRTUALDIR)/bin/activate; { pip install -Ur requirements.txt; python -V; pip --version; }
	@touch $(VIRTUALDIR)/bin/activate
