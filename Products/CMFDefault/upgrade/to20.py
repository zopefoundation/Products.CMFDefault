##############################################################################
#
# Copyright (c) 2009 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Upgrade steps to CMFDefault 2.0.

$Id$
"""
import logging

from Acquisition import aq_base

from Products.CMFCore.utils import getToolByName
from Products.CMFDefault.MetadataTool import _DCMI_ELEMENT_SPECS
from Products.CMFDefault.MetadataTool import MetadataSchema


def check_dcmi_metadata(tool):
    """1.6.x to 2.0.0 upgrade step checker
    """
    metadata_tool = getToolByName(tool, 'portal_metadata')
    return getattr(aq_base(metadata_tool), 'element_specs', None) is not None

def upgrade_dcmi_metadata(tool):
    """1.6.x to 2.0.0 upgrade step handler
    """
    logger = logging.getLogger('GenericSetup.upgrade')
    metadata_tool = getToolByName(tool, 'portal_metadata')
    old_specs = getattr(metadata_tool, 'element_specs', None)
    if old_specs is not None:
        del metadata_tool.element_specs
        dcmi = metadata_tool._DCMI = MetadataSchema('DCMI', _DCMI_ELEMENT_SPECS)
        for element_id, old_spec in old_specs.items():
            new_spec = dcmi.getElementSpec(element_id)
            for typ, policy in old_spec.listPolicies():
                if typ is not None:
                    new_spec.addPolicy(typ)
                tp = new_spec.getPolicy(typ)
                tp.edit( is_required=policy.isRequired()
                       , supply_default=policy.supplyDefault()
                       , default_value=policy.defaultValue()
                       , enforce_vocabulary=policy.enforceVocabulary()
                       , allowed_vocabulary=policy.allowedVocabulary()
                       )
    logger.info('Dublin Core metadata definition updated.')
