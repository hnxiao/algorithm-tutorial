import unittest    

from mod2 import Mod2
from math import *

class SquareMatrixError(Exception):
    """ An exception class for SquareMatrix """
    pass

class SquareMatrix(object):
    """ Python square mod2 matrix class with
    basic operations and operator overloading """
    
    def __init__(self, n, init=True):
        if init:
            self.rows = [[Mod2(0) for c in range(n)] for r in range(n)]
        else:
            self.rows = []
            
        self.n = n
        
    def __getitem__(self, idx):
        return self.rows[idx]

    def __setitem__(self, idx, item):
        self.rows[idx] = item
        
    def __str__(self):
        s='\n'.join([' '.join([str(item) for item in row]) for row in self.rows])
        return s + '\n'

    def __repr__(self):
        s=str(self.rows)
        rank = str(self.n)
        rep="Square Matrix: \"%s\", rank: \"%s\"" % (s,rank)
        return rep
                         
    def __eq__(self, mat):
        """ Test equality """
        return (self.rows == mat.rows)
        
    def __add__(self, mat):
        """ Add this matrix to another matrix and return the result.
        Don't modify this matrix."""
        
        if self.n != mat.n:
            raise SquareMatrixError, "Adding matrices of different size."

        result = SquareMatrix(self.n)
        result.rows = [ [a + b for (a, b) in zip(self.rows[r], mat[r])]
                        for r in range(self.n) ]

        return result
        
    def __sub__(self, mat):
        # In Mod2 adding is the same as subtracting.
        return self + mat

    def __mul__(self, mat):
        """NAIVE SQUARE MULTIPLICATION ALGORITHM:
        
        Multiply this matrix by another matrix and return the result.
        Don't modify this matrix."""
        
        if self.n != mat.n:
            raise SquareMatrixError, "Multiplying matrices of different size."
        
        result = SquareMatrix(self.n)
        
        for i in range(self.n):
            for j in range(self.n):
                for k in range(self.n):
                    result[i][j] += self.rows[i][k] * mat[k][j]

        return result

    def divide(self):

        n = self.n
        
        m11 = SquareMatrix(n/2)
        m12 = SquareMatrix(n/2)
        m21 = SquareMatrix(n/2)
        m22 = SquareMatrix(n/2)

        m11.rows = [[self.rows[r][c] for c in range(n/2)]
                    for r in range(n/2)]
        m12.rows = [[self.rows[r][c] for c in range(n/2, n)] 
                    for r in range(n/2)]
        m21.rows = [[self.rows[r][c] for c in range(n/2)]
                    for r in range(n/2, n)]
        m22.rows = [[self.rows[r][c] for c in range(n/2, n)] 
                    for r in range(n/2, n)]
                         
        return [[m11, m12], [m21, m22]]
        
    def strassen(self, mat):
        """STRASSEN MULTIPLICATION:
        
        Multiply this matrix by another matrix and return the result.
        Don't modify this matrix."""
        
        if floor(log(self.n, 2)) != log(self.n, 2):
            raise SquareMatrixError, "Please use an exact-power-of-two size."
        
        if self.n != mat.n:
            raise SquareMatrixError, "Multiplying matrices of different size."
        
        if self.n == 1:
            return self * mat
        
        # divide self.rows and mat.rows
        a = self.divide()
        b =  mat.divide()
        
        # add/subtract to get 10 necessary matrices
        s = [b[0][1] - b[1][1], a[0][0] + a[0][1],
             a[1][0] + a[1][1], b[1][0] - b[0][0],
             a[0][0] + a[1][1], b[0][0] + b[1][1],
             a[0][1] - a[1][1], b[1][0] + b[1][1],
             a[0][0] - a[1][0], b[0][0] + b[0][1]]
        
        # recursion: the seven matrix products
        p = [a[0][0].strassen(s[0]),
             s[1].strassen(b[1][1]),
             s[2].strassen(b[0][0]),
             a[1][1].strassen(s[3]),
             s[4].strassen(s[5]),
             s[6].strassen(s[7]),
             s[8].strassen(s[9])]
        
        # submatrices of result
        subs = [  [p[4] + p[3] - p[1] + p[5], p[0] + p[1]],
                  [p[2] + p[3], p[4] + p[0] - p[2] - p[6]]  ]

        # combine        
        result = SquareMatrix.fromSubmatrices(subs)
                
        return result

    @classmethod
    def _makeSquareMatrix(cls, rows):

        n = len(rows)
        # Validity check
        if any([len(row) != n for row in rows]):
            raise SquareMatrixError, "Not a square matrix."
        mat = SquareMatrix(n, init=False)
        mat.rows = [[Mod2(e) for e in row] for row in rows]
        
        return mat
                    
    @classmethod
    def fromList(cls, listoflists):
        """ Create a matrix by directly passing a list of lists.
        
        E.g: SquareMatrix.fromList([[1 2 3], [4,5,6], [7,8,9]])"""

        rows = listoflists[:]
        return cls._makeSquareMatrix(rows)
    
    @classmethod    
    def fromSubmatrices(cls, subs):
        """ Create a matrix by directly passing a list of 4 submatrices."""
        
        # subs are of type SquareMatrix
        sub_n = subs[0][0].n
                
        rs  = [subs[0][0][row] + subs[0][1][row] for row in range(sub_n)] + [
               subs[1][0][row] + subs[1][1][row] for row in range(sub_n)]
        
        rows = [[e.value for e in row] for row in rs]
              
        return cls._makeSquareMatrix(rows)
        
class SquareMatrixTests(unittest.TestCase):

    def testAdd(self):
        m1 = SquareMatrix.fromList([ [0, 1, 0], 
                                     [1, 0, 1], 
                                     [1, 0, 1] ])
        m2 = SquareMatrix.fromList([ [1, 1, 1], 
                                     [0, 1, 0], 
                                     [1, 1, 1] ])        
        m3 = m1 + m2
        self.assertTrue(m3 == SquareMatrix.fromList([ [1, 0, 1],
                                                      [1, 1, 1],
                                                      [0, 1, 0] ]))

    def testMul(self):
        m1 = SquareMatrix.fromList([ [0, 1, 0, 0], 
                                     [1, 0, 1, 1], 
                                     [0, 0, 1, 0],
                                     [0, 1, 1, 0] ])
        m2 = SquareMatrix.fromList([ [1, 1, 1, 1], 
                                     [0, 1, 0, 0], 
                                     [1, 1, 1, 0],
                                     [0, 0, 0, 0] ])        
        m3 = m1 * m2
        self.assertTrue(m3 == SquareMatrix.fromList([ [0, 1, 0, 0],
                                                      [0, 0, 0, 1],
                                                      [1, 1, 1, 0],
                                                      [1, 0, 1, 0] ]))

    def testStrassen(self):
        m1 = SquareMatrix.fromList([ [0, 1, 0, 0], 
                                     [1, 0, 1, 1], 
                                     [0, 0, 1, 0],
                                     [0, 1, 1, 0] ])
        m2 = SquareMatrix.fromList([ [1, 1, 1, 1], 
                                     [0, 1, 0, 0], 
                                     [1, 1, 1, 0],
                                     [0, 0, 0, 0] ])        
        m3 = m1.strassen(m2)
        self.assertTrue(m3 == SquareMatrix.fromList([ [0, 1, 0, 0],
                                                      [0, 0, 0, 1],
                                                      [1, 1, 1, 0],
                                                      [1, 0, 1, 0] ]))



if __name__ == "__main__":
    unittest.main()
