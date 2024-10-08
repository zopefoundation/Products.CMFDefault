Products.CMFDefault Changelog
=============================

2.4.0 (unreleased)
------------------

- Added support for Zope 4

- Removed support for Zope 2.13 and ZServer-based sites


2.3.0 (2020-02-04)
------------------

- Add data-base-url attribute in body tag
  (`Products.CMFPlone#2051
  <https://github.com/plone/Products.CMFPlone/issues/2051>`_)

- Changed `DiscussionItem.in_reply_to` null value from None to empty string,
  to use the same type and allow indexing in newer versions of BTree.

- page templates: Improved Chameleon support.
  If five.pt is installed, its zcml configuration is included.

- interfaces: Fixed dotted names by setting __module__ explicitly.

- profiles and upgrade: Added new `Members Folder` and `Home Folder` types.
  This allows to customize member area creation and behavior by modifying the
  special portal types. The 'createMemberContent' hook is deprecated. An
  additional upgrade step helps to convert the portal type of existing members
  and home folders. If you don't run the two upgrade steps and don't add a
  `Home Folder` portal type, you get backwards compatible behavior.

- content: Added `cmf.folder.home` factory for creating home folders.

- browser views: Synced view names with the names used in type Actions.

- profiles and upgrade: Modified Method Aliases used in type Actions.
  Added upgrade steps for default profile and views_support profile.

- Actions: Added invisible 'global/search_form' and 'global/search' Actions.
  The URLs of the search form and the search results pages are no longer
  hard-wired in main_template, making it easier to switch to browser views.

- Fixed AttributeError for allowDiscussion when importing a
  GenericSetup structure tarball.
  See https://bugs.launchpad.net/zope-cmf/+bug/1042836/

- browser views: Added 'registered_email' and 'password_email' views.
  Please note that these views override the corresponding skin methods. If you
  want to use customized versions from the skins tool you have to make sure
  these views are not registered. It is recommended to customize the browser
  views instead.

- RegistrationTool: Improved 'mailPassword' and 'registeredNotify' methods.
  Mail templates can now be views. 'mail_password_response' is no longer
  required, using the return value of 'mailPassword' is deprecated. Sending
  mails immediately is now enforced to allow better error handling.

- PropertiesTool: Fixed editing single properties.

- browser views: Fixed zope.formlib 4.1 compatibility.

- Add 'locales' as extras_require in setup.py, with dependency on
  zope.app.locales.


2.3.0-beta2 (2012-03-31)
------------------------

- skins and upgrade: Fixed broken reconfig_form.
  Added upgrade step for fixing site properties corrupted by that form.


2.3.0-beta (2012-03-21)
-----------------------

- tools: Converted all tools into local utilities.

- skins and browser views: setRedirect now checks Action conditions.

- Actions: Added 'global/members_register' Action for redirects.
  It is similar to 'user/join', but adjusted for user managers.

- MemberDataTool: Changed property modes to 'w' and added 'fullname' property.

- File and Image: Made sure `id` is always an attribute and not a method.
  Some old instances use `__name__` instead of `id`. Use getId() to get always
  the correct ID.

- DublinCore: 'getMetadataHeaders' now returns the Type ID, not the Type title.
  This avoids conflicts between unicode messages and encoded non-ASCII strings.

- Only test reStructuredText functionality under Zope 2.13 and before.

- Document: Improved 'manage_FTPget' method.
  HTML responses can now be rendered by a view.

- Removed ``five.formlib`` dependency. ``zope.formlib`` is now used directly.

- profiles: Added default settings for the member data tool.

- upgrade: Added upgrade step for member data tool settings.

- skins and browser views: Fixed 'login_time' handling.
  Should be working with string and DateTime values because the MemberDataTool
  settings might be inconsistent.

- browser views: Added SettingsEditFormBase.
  This can be used for edit forms for global settings.

- profiles and upgrade: Added support for using the new OFS UserFolder class.

- views: Added Unauthorized exception view.
  This replaces CookieCrumbler's old redirect support.

- skins: Removed unused styles from css.

- SyndicationTool: Updated to produce RSS 2.0. Uses an adapter for
  syndication information.

- Require at least Zope 2.13.12.


2.2.2 (2010-10-31)
------------------

- Content-type setting was incorrectly transcribed from getMailGlobals 
  which meant that content-type=' ;charset-utf-8' was set on browser 
  views which is incorrect (backport from trunk).

- Utility class used for wrapping items for display (backport from 
  trunk).

- Fixed Chameleon incompatibilities in some templates.


2.2.1 (2010-07-04)
------------------

- Require at least Zope 2.12.3 and always use the five.formlib extension.

- Removed testing dependency on zope.app.testing.

- Deal with deprecation warnings for Zope 2.13.

- Use the standard libraries doctest module.

- upgrade: Added 2 more upgrade steps for upgrades from CMF 2.0.
  Upgrades from unmodified CMF 2.0 and CMF 2.1 sites are now fully covered,
  customized or older CMF sites might require additional manual upgrades.


2.2.0 (2010-01-04)
------------------

- Use five.formlib in favor of Products.Five.formlib if it is available.

- skins: Fixed skin changing for logged in members.

- Upgrade steps: Merged faulty utility registration fixup script,
  tool utility registration and new-style actions upgrade from 
  an older migration script in Products.CMFCore for pre-2.1.0 
  instances into GenericSetup upgrade steps

- WorkflowTool/DiscussionItem: Create a set of GenericSetup 
  upgrade steps to instantiate the new single-state workflow 
  for Discussion Items and associate it with the content type.

- MetadataTool: Replaced write-on-read upgrade for the Dublin Core
  metadata definitions with a set of GenericSetup upgrade steps.


2.2.0-beta (2009-12-06)
-----------------------

- MetadataTool: Improved tool initialization.
  This prevents write-on-read behavior of newly created tool instances.

- views: Improved ContentAddFormBase.
  Permissions and container constraints are now checked by the '__call__'
  method. There is no need to add security declarations for derived add forms.

- upgrade: Added more upgrade steps.
  There is now support for upgrading the step registrations in the setup tool,
  the columns in the catalog tool and the icons in the actions tool and
  in workflow definitions.

- upgrade: Improved upgrade step for type properties.
  Please re-run it if you already used an older version of this step.

- Skins and browser views: Replaced 'getIcon' by 'getIconURL' calls.


2.2.0-alpha (2009-11-13)
------------------------

- Got rid of redundant icon related type info properties.
  (https://bugs.launchpad.net/zope-cmf/+bug/397795)

- Folder views: Rebuilt the CMF folder views based on 
  zope.formlib.

- SkinnedFolder: Adjusted implementation to PortalFolder changes.

- moved the Zope dependency to version 2.12.0b3dev

- Add views: The standard INameChooser adapter from Products.Five 
  fails with BTreeFolder-based portal folders, so we need our own.
  (https://bugs.launchpad.net/zope-cmf/+bug/377562)

- Actions: Utilize the new link_target attribute for the
  final rendered link tag's "target" attribute
  (https://bugs.launchpad.net/zope-cmf/+bug/376951)

- MembershipTool: Support members folder paths to folders deeper in 
  the portal folder hierarchy by allowing to specify either a 
  simple name (as before), or a relative path within the portal 
  in the membership tool "Configuration" ZMI tab.

- profiles: Explicitly initialize the workflow manager_bypass value
  which has been added to DCWorkflow.
  (https://bugs.launchpad.net/zope-cmf/+bug/308947)

- No longer rely on the PageTemplates.GlobalTranslationService but use
  zope.i18n.translate directly.

- Cleaned up / normalized imports:

  o Don't import from Globals;  instead, use real locations.

  o Make other imports use the actual source module, rather than an
    intermediate (e.g., prefer importing 'ClassSecurityInfo' from
    'AccessControl.SecurityInfo' rather than from 'AccessControl').

  o Avoid relative imports, which will break in later versions of Python.

- profiles: Added add view expressions to content type definitions.

- skins/zpt_generic/permalink.py: fix typos, wrap object correctly.
  See: https://bugs.launchpad.net/bugs/299058 .

- upgrade: Added basic upgrade steps.
  So far they just allow to upgrade the site object and types.

- DiscussionTool: Make sure to only ask "real" content for their type
  information when checking whether discussions are allowed or not.

- skins: Display add actions in the main_template.
  Using folder_factories is now deprecated.

- views: Added FallbackAddView.
  This add form works with any portal type. It just asks for the ID.

- formlib widgets: Added special input widget for object IDs.

- main_template: Display action icons, thereby replacing the separate
  CMFActionIcons product.

- Portal: Add a flag to toggle the display of action icons.

- Workflow GenericSetup definition: Add icon URL expressions to the 
  worklist and transition action definitions.

- Content type and action GenericSetup profiles: Add an icon URL expression 
  to the content type and actions definitions.

- File and Image: Move the call to the underlying OFS rendering to the
  end of their own index_html methods to ensure the caching policy
  manager can set headers in all situations.
  (https://bugs.launchpad.net/zope-cmf/+bug/161723)

- Discussions: Replaced the old (and no longer working) way to force 
  Discussion Items into published state by default with a real 
  single-state workflow so they are put into published state correctly.
  (https://bugs.launchpad.net/zope-cmf/+bug/161720)

- ZMI: Prevent users from creating content through the ZMI by hiding the
  entry for "CMFDefault Content".

- SyndicationTool: Removed obsolete documentation link from the
  Overview ZMI tab.
  (https://bugs.launchpad.net/zope-cmf/+bug/185090)
  
- Document: Fixed Zope 2.12 compatibility.
  zope.structuredtext is now used instead of StructuredText.

- Image, File:  make ZMI "edit" view work.

- views: Added ContentAddFormBase and several content add views.
  This shows how form-driven content creation works. The content is created
  without using the constructor methods provided by the types tool.

- DublinCore: Modified the 'addCreator' implementation.
  It no longer depends on the membership tool.

- DiscussionItem: Removed 'addDiscussionItem' function.
  This was dead code. 'createReply' is used for adding DiscussionItems.

- content: Factories no longer sends add events.

- profiles: Removed obsolete local import and export step registrations.

- setup handler: Improved 'various' import step.
  Added flag file check and global registration.

- Document and NewsItem: It is now possible to register a utility
  (ILinebreakNormalizer) that can normalize line breaks upon editing or
  rendering out to FTP.
  (http://www.zope.org/Collectors/CMF/174)

- Document and NewsItem: Added a format choice for ReStructuredText.
  (http://www.zope.org/Collectors/CMF/485)

- interfaces: Removed deprecated oldstyle interfaces.


2.1.2 (2008-09-13)
------------------

- SyndicationTool: Removed obsolete documentation link from the
  Overview ZMI tab.
  (https://bugs.launchpad.net/zope-cmf/+bug/185090)


2.1.2-beta (2008-08-26)
-----------------------

- completed devolution from monolithic CMF package into its component
  products that are distributed as eggs from PyPI.

- File, Image:  Make the ZMI edit tab work.

- DiscussionItem: Fixed indexing of 'in_reply_to'.


2.1.1 (2008-01-06)
------------------

- PropertiesTool: Fix a faulty manage_changeProperties
  invocation which broke the 'Reconfigure Portal' screen
  (https://bugs.launchpad.net/zope-cmf/+bug/174246)


2.1.1-beta(2007-12/29)
----------------------

- Testing: Derive test layers from ZopeLite layer if available.

- CMFDefault profiles: Fixed some dependencies in import_steps.xml.

- utils: The email validation would reject addresses where
  the domain part started with a single letter element.
  (http://www.zope.org/Collectors/CMF/495)

- skins: Prevented the getMainGlobals script to fail if not
  content-type header is set.


2.1.0 (2007-08-08)
------------------

- Fixed all componentregistry.xml files to use plain object paths and strip
  and slashes. GenericSetup does only support registering objects which are
  in the site root.

- utils: Allow email addresses with all-numeric domain names.
  The RFCs do not support them but they do exist.
  (http://dev.plone.org/plone/ticket/6773)


2.1.0-beta2 (2007-07-12)
------------------------

- moved the Zope dependency to version 2.10.4

- Remove antique usage of marker attributes in favor of interfaces,
  leaving BBB behind for places potentially affecting third-party code.
  (http://www.zope.org/Collectors/CMF/440)

- Add POST-only protections to security critical methods.
  http://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2007-0240)

- Use a utility, registered for
  'Products.CMFDefault.interfaces.IHTMLScrubber', to perform scrubbing
  of HTML;  fall back to the old, hard-wired behavior.
  (http://www.zope.org/Collectors/CMF/452)

- Favorite: Fixed UID handling broken in 2.1.0-beta.

- Removed CMFUid dependency inadvertently added in 2.1.0-beta.

- GS integration: Adjusted factory.py to new GenericSetup version.


2.1.0-beta (2007-03-09)
-----------------------

- moved the Zope dependency to verson 2.10.2

- Tool lookup and registration is now done "the Zope 3 way" as utilities, see
  http://svn.zope.org/CMF/branches/2.1/docs/ToolsAreUtilities.stx?view=auto

- Document: Added two new methods for safety belt handling.

- MembershipTool: when using an object without a __nonzero__ but with a 
  __len__ (ala CMFBTreeFolder) as a member folder, the createMemberArea 
  method would believe there was no members folder if the folder was
  empty, and so would fail (change "not membersfolder" to
  "membersfolder is not None") .

- File and Image: Restored ZMI Cache tab which was lost in CMF 1.6.


2.1.0-alpha2 (2006-11-23)
-------------------------

- moved the Zope dependency to version 2.10.1

- Fixed test breakage induced by use of Z3 pagetemplates in Zope 2.10+.

- browser views: Added some zope.formlib based forms.

- testing: Added test layers for setting up ZCML.

- Added zope.formlib support.
  This includes some CMF specific base classes and an 'EmailLine' field.

- utils: Added 'checkEmailAddress' function.

- Portal: Added 'email_charset' property.

- utils: Added 'makeEmail' function.

- Image and File: Overridden index_html methods
  add Cache Policy Manager-awareness and thus bring these implementations
  in line with CMFCore.FSFile and CMFCore.FSImage
  (http://www.zope.org/Collectors/CMF/454)

- RegistrationTool: Fixed too restrictive email checking.
  The new 'checkEmailAddress' function is now used.

- skins: Fixed encoding issues in welcome and reminder emails.
  'password_email' and 'registered_email' now encode their return value
  correctly, using 'email_charset' and the new 'makeEmail' function.


2.1.0-alpha (2006-10-09)
------------------------

- skins: Changed encoding of translated portal_status_messages.
  Now getBrowserCharset is used to play nice with Five forms. Customized
  setRedirect and getMainGlobals scripts have to be updated.

- Profiles: All profiles are now registered by ZCML.

- ZClasses: Removed unmaintained support for ZClasses.
  Marked the 'initializeBases*' methods as deprecated.

- Content: Added IFactory utilities for all content classes.
  They are now used by default instead of the old constructor methods.

- Content: All content classes are now registered by ZCML.
  ContentInit is still used to register oldstyle constructors.

- setup handlers: Removed support for CMF 1.5 CMFSetup profiles.

- utils: Added getBrowserCharset function.
  Returns the charset preferred by the browser. Strings encoded with this
  charset are decoded correctly by Five.browser.decode.processInputs.

- Favorite: Added 'handleFavoriteAddedEvent' subscriber.
  This replaces the 'manage_afterAdd' hook and some code in 'addFavorite'.


Earlier releases
----------------

For a complete list of changes before version 2.1.0-alpha, see the HISTORY.txt
file on the CMF-2.1 branch:
http://svn.zope.org/CMF/branches/2.1/HISTORY.txt?view=auto

