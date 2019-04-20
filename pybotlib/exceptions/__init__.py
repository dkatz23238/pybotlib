class Error(Exception):
   """Base class for other exceptions"""
   pass

class NoElementsSatisfyConditions(Error):
   """Raised when find_by_tag_and_attr results in an empty list"""
   pass