# -*- coding: utf-8 -*-
"""Name-to-Class maps.

Checks and Notifiers are given aliases, so that they can be represented during
inter-service communications, such as those of between master and workers. This
creates a consistent language and can be useful for different-langauge
implementations.
"""

from gefion import checks, notifiers

CHECKS = {'port': checks.PortCheck}

NOTIFIERS = {'telegram': notifiers.TelegramNotifier}
