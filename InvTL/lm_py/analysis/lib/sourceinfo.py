"""
Provides get_source_info(<filename>) function to determine the format
(free|fixed|strict|pyf) of a Fortran file.

-----
Permission to use, modify, and distribute this software is given under the
terms of the NumPy License. See http://scipy.org.

NO WARRANTY IS EXPRESSED OR IMPLIED.  USE AT YOUR OWN RISK.
Author: Pearu Peterson <pearu@cens.ioc.ee>
Created: May 2006
-----
"""

def get_source_info(filename):
    """
    Determine if fortran file is
      - in fix format and contains Fortran 77 code    -> return False, True
      - in fix format and contains Fortran 90 code    -> return False, False
      - in free format and contains Fortran 90 code   -> return True, False
      - in free format and contains signatures (.pyf) -> return True, True
    """
    return boolean(),boolean()


