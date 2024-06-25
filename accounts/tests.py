# from django.test import TestCase

# # Create your tests here.
# class StudentManager(models.Manager):
# 	def create_user(self , email , password = None):
# 		if not email or len(email) <= 0 :
# 			raise ValueError("Email field is required !")
# 		if not password :
# 			raise ValueError("Password is must !")
# 		email = email.lower()
# 		user = self.model(
# 			email = email
# 		)
# 		user.set_password(password)
# 		user.save(using = self._db)
# 		return user
	
# 	def get_queryset(self , *args, **kwargs):
# 		queryset = super().get_queryset(*args , **kwargs)
# 		queryset = queryset.filter(type = UserAccount.Types.STUDENT)
# 		return queryset	
		
# class Student(UserAccount):
# 	class Meta :
# 		proxy = True
# 	objects = StudentManager()
	
# 	def save(self , *args , **kwargs):
# 		self.type = UserAccount.Types.STUDENT
# 		self.is_student = True
# 		return super().save(*args , **kwargs)
	
# class TeacherManager(models.Manager):
#     	def get_queryset(self , *args , **kwargs):
# 		queryset = super().get_queryset(*args , **kwargs)
# 		queryset = queryset.filter(type = UserAccount.Types.TEACHER)
# 		return queryset

# 	def create_user(self , email , password = None):
# 		if not email or len(email) <= 0 :
# 			raise ValueError("Email field is required !")
# 		if not password :
# 			raise ValueError("Password is must !")
# 		email = email.lower()
# 		user = self.model(
# 			email = email
# 		)
# 		user.set_password(password)
# 		user.save(using = self._db)
# 		return user
		

	
# class Teacher(UserAccount):
# 	class Meta :
# 		proxy = True
# 	objects = TeacherManager()
	
# 	def save(self , *args , **kwargs):
# 		self.type = UserAccount.Types.TEACHER
# 		self.is_teacher = True
# 		return super().save(*args , **kwargs)
