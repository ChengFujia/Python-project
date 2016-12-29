# coding: utf-8
import check
import unittest

class TestCheck(unittest.TestCase):
	def test_regular(self):
		rv = check.password("qwertyu")	
		self.assertTrue(repr(rv) == "simple")
		# two ways both meanful
		#self.assertTrue('Regular' in rv.message)
		self.assertTrue('Regular' in str(rv))
	def test_by_step(self):
       	 	rv = check.password('abcdefg')
        	self.assertTrue(repr(rv) == 'simple')
        	self.assertTrue('Regular' in rv.message)

    	def test_common(self):
        	rv = check.password('password')
        	self.assertTrue(repr(rv) == 'simple')
        	self.assertTrue('Common' in rv.message)

    	def test_medium(self):
        	rv = check.password('tdnwh01')
        	self.assertTrue(repr(rv) == 'medium')
        	self.assertTrue('Not Strong Enough' in rv.message)

    	def test_strong(self):
        	rv = check.password('tdnWwh01.')
        	self.assertTrue(repr(rv) == 'strong')
        	self.assertTrue('Perfect' in rv.message)

	def test_email(self):
		rv = check.Email('adc11@qq.com')
		self.assertTrue(rv.isValiEmail() == True)

	def test_emailType(self):
		rv = check.Email("adc@qq.com")
		self.assertTrue(rv.getEmailType() == 'qq')

if __name__ == "__main__":
	unittest.main()
