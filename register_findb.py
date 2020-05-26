#!/usr/bin/env python
"""
quickly register 'Finda/asset.db' into Finda
"""
from Finda import fd_manager

fd_manager.FdMultiController.fd_register('asset')
