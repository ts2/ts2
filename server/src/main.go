package main

import (
	"ts2"
	"fmt"
	"encoding/json"
	"flag"
)

func main() {
	simJson := flag.String("load", "", "A JSON string with the simulation definition to load")
	flag.Parse()
	json.Unmarshal([]byte(*simJson), ts2.Sim)
	fmt.Println("Press Ctrl-C to end")
	for {
	}
}
