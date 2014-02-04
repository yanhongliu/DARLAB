# __init__.py
#
# Copyright (c) 2004 Michael Hobbs
#
# This file is part of Candygram.
#
# Candygram is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation; either version 2.1 of the License, or
# (at your option) any later version.
#
# Candygram is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Candygram; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

"""Erlang concurrency primitives"""

__revision__ = '$Id: __init__.py,v 1.8 2004/10/21 15:49:26 hobb0001 Exp $'


from candygram.main import spawn, spawnLink, self, self_, exit, link, unlink, \
		processFlag, processes, isProcessAlive, send, ExitError
from candygram.process import Process
from candygram.receiver import Receiver, Message
from candygram.pattern import Any, AnyRemaining


__all__ = ['spawn', 'spawnLink', 'self', 'self_', 'exit', 'link', 'unlink',
		'processFlag', 'processes', 'isProcessAlive', 'send', 'ExitError',
		'Process', 'Receiver', 'Message', 'Any']
