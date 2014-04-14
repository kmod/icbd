import import_test.a as p

p # 0 module 'a'
import_test # e 0
import import_test
import_test # 0 module 'import_test'
import_test.a # 12 module 'a'
