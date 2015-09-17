
import unittest
from . import shadermixer
import itertools

class TestShaderMixer(unittest.TestCase):

    def assertCode(self, expected_, actual_):
        expected = expected_.strip()
        actual = actual_.strip()
        expected = [l.strip() for l in expected.splitlines()]
        actual = [l.strip() for l in actual.splitlines()]
        
        for linenr, (exp, act) in enumerate(itertools.zip_longest(expected, actual), 1):
            if exp == None:
                print(actual_)
                self.fail("Got unexpected additional line: {!r}".format(act))
            if act == None:
                print(actual_)
                self.fail("Expected additional line: {!r}".format(exp))
            if exp != act:
                print(actual_)
                self.fail(("Difference on line {nr}. " + 
                                 "Expected {exp!r}, got {act!r}.").format(
                                    nr = linenr,
                                    exp = exp,
                                    act = act
                                 ))

    def test_no_args(self):
        
        src = """
            void main(){
            }
        """

        expected = """
            void renamed(){
            }
        """

        actual, args = shadermixer.parse(src, "renamed")
        
        self.assertCode(expected, actual)
        self.assertEqual(args, [])
        
    def test_in(self):
        src="void main(in float a)"
        _, args = shadermixer.parse(src, "renamed")
        self.assertEqual(args, [("in", "float", "a", ())])
        
    def test_inout(self):
        src="void main(inout float a)"
        _, args = shadermixer.parse(src, "renamed")
        self.assertEqual(args, [("inout", "float", "a", ())])
        
    def test_out(self):
        src="void main(out float a)"
        _, args = shadermixer.parse(src, "renamed")
        self.assertEqual(args, [("out", "float", "a", ())])
        
    def test_array(self):
        src="void main(out float a[4])"
        _, args = shadermixer.parse(src, "renamed")
        self.assertEqual(args, [("out", "float", "a", (4,))])
        
    def test_multiarray(self):
        src="void main(out float a[4][3])"
        _, args = shadermixer.parse(src, "renamed")
        self.assertEqual(args, [("out", "float", "a", (4,3))])
        
    def test_array_spaces(self):
        src="void main(out float a [4][3])"
        _, args = shadermixer.parse(src, "renamed")
        self.assertEqual(args, [("out", "float", "a", (4,3))])  
        
    def test_array_spaces2(self):
        src="void main(out float a[4] [3])"
        _, args = shadermixer.parse(src, "renamed")
        self.assertEqual(args, [("out", "float", "a", (4,3))])
        
    def test_array_spaces3(self):
        src="void main(out float a[4 ][ 3])"
        _, args = shadermixer.parse(src, "renamed")
        self.assertEqual(args, [("out", "float", "a", (4,3))])
        
    def test_args(self):
        src="void main(in vec2 a, out vec3 b)"
        _, args = shadermixer.parse(src, "renamed")
        self.assertEqual(args, [("in", "vec2", "a", ()), ("out", "vec3", "b", ())])
    
    def test_prepare(self):
        src = """
        void main(){}
        """
        expected = """
        void _renamed(){}
        
        void renamed(){
             _renamed();
        }
        """
        actual = shadermixer.prepare(src, "renamed", [], False, False)
        self.assertCode(expected, actual)
        
    def test_prepare_explicitin(self):
        src = """
        void main(in vec2 a){}
        """
        expected = """
        void _renamed(in vec2 a){}
        
        void renamed(in vec2 a){
             _renamed(a);
        }
        """
        actual = shadermixer.prepare(src, "renamed", [("in", "vec2", "a", ())], False, False)
        self.assertCode(expected, actual)
        
    def test_prepare_explicitout(self):
        src = """
        void main(out vec2 a){}
        """
        expected = """
        void _renamed(out vec2 a){}
        
        void renamed(out vec2 a){
             _renamed(a);
        }
        """
        actual = shadermixer.prepare(src, "renamed", [("out", "vec2", "a", ())], False, False)
        self.assertCode(expected, actual)
        
    def test_prepare_implicitin(self):
        src = """
        void main(in vec2 a){}
        """
        expected = """
        in vec2 U_a;
        
        void _renamed(in vec2 a){}
        
        void renamed(){
             _renamed(U_a);
        }
        """
        actual = shadermixer.prepare(src, "renamed", [], False, False)
        self.assertCode(expected, actual)
        
    def test_prepare_implicitarray(self):
        src = """
        void main(in vec2 a){}
        """
        expected = """
        in vec2 U_a[];
        
        void _renamed(in vec2 a){}
        
        void renamed(in int in_index){
             _renamed(U_a[in_index]);
        }
        """
        actual = shadermixer.prepare(src, "renamed", [], True, False)
        self.assertCode(expected, actual)
        
    def test_prepare_mixin(self):
        src = """
        void main(in vec2 a, in float b, out vec2 c, out float d){}
        """
        expected = """
        in float U_b[];
        out float U_d[];
        
        void _renamed(in vec2 a, in float b, out vec2 c, out float d){}
        
        void renamed(in vec2 a, out vec2 c, in int in_index, in int out_index){
             _renamed(a, U_b[in_index], c, U_d[out_index]);
        }
        """
        actual = shadermixer.prepare(src, "renamed", [("in", "vec2", "a", ()), ("out", "vec2", "c", ())], True, True)
        self.assertCode(expected, actual)
        