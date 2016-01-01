package ts2

import (
	"testing"
	"io/ioutil"
)

func (a DelayGenerator) equals(b DelayGenerator) bool {
	for i := 0; i < len(a.data); i++ {
		for j := 0; j < 3; j++ {
			if a.data[i][j] != b.data[i][j] {
				return false
			}
		}
	}
	return true
}

func assertTrue(t *testing.T, expr bool, msg string) {
	if !expr {
		t.Errorf("%v: expression is false", msg)
	}
}

func assertEqual(t *testing.T, a interface{}, b interface{}, msg string) {
	if a != b {
		t.Errorf("%v: %v(%T) is not equal to %v(%T)", msg, a, a, b, b)
	}
}

func loadSim() []byte {
	data, _ := ioutil.ReadFile("test_data/demo.json")
	return data
}