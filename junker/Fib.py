__author__='Vasanth'
__Date__='2014-05-20'
"""
The Script which describes the fibonacci series program in structured way
"""
class Fibonacci:
	def __init__(self,number):
		"""
		Added some doc strings in constructor
		"""
		self.number=number
		self.a=0
		self.b=1
		self.c=0

	def CalculateFib(self):
		print "_______Fibonacci for a given range(%d) is __________" %(self.number)
		for i in range(self.number):
			self.c=self.a+self.b
			self.b=self.a
			self.a=self.c
			print self.c,


if __name__=='__main__':
	Input=input("Enter the value to which the number have to displayed")
	fib=Fibonacci(Input)
	fib.CalculateFib()
