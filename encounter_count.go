// Reimplementation of the Python script with the same name.
// Refer to the Python script for documentation.

package main

import (
	"bufio"
	"flag"
	"fmt"
	"os"
	"sort"
	"strconv"
	"strings"
)

func main() {
	u := flag.Bool("u", false, "Unique encounters (not total).")
	flag.Parse()

	// read contacts from stdin
	contacts := []Contact{}
	scanner := bufio.NewScanner(os.Stdin)
	for scanner.Scan() {
		fields := strings.Split(strings.TrimSpace(scanner.Text()), ",")
		node1, node2 := fields[0], fields[1]
		start, _ := strconv.Atoi(fields[2])
		contacts = append(contacts, Contact{node1, node2, start})
	}

	// calculate results
	var results []IntPair
	if *u {
		results = unique(contacts)
	} else {
		results = total(contacts)
	}

	// write results to stdout
	for _, r := range results {
		fmt.Println(strings.Join([]string{
			strconv.Itoa(r.one),
			strconv.Itoa(r.two)},
			","))
	}
}

func total(contacts []Contact) []IntPair {
	sort.Sort(ByStart(contacts))
	counts := []IntPair{}
	start := contacts[0].start
	count := 0
	current_time := contacts[0].start
	for _, c := range contacts {
		if current_time != c.start {
			counts = append(counts, IntPair{current_time - start,
				count})
		}
		count++
		current_time = c.start
	}
	counts = append(counts, IntPair{current_time - start, count})
	return counts
}

func unique(contacts []Contact) []IntPair {
	sort.Sort(ByStart(contacts))
	counts := []IntPair{}
	start := contacts[0].start
	count := 0
	current_time := contacts[0].start
	// key -> sorted NodePair
	node_pairs := make(map[NodePair]bool)
	for _, c := range contacts {
		if current_time != c.start {
			counts = append(counts, IntPair{current_time - start,
				count})
		}
		nodes := []string{c.node1, c.node2}
		sort.Strings(nodes)
		pair := NodePair{nodes[0], nodes[1]}
		if !node_pairs[pair] {
			count++
			node_pairs[pair] = true
		}
		current_time = c.start
	}
	counts = append(counts, IntPair{current_time - start, count})
	return counts
}

type IntPair struct {
	one, two int
}

type Contact struct {
	node1, node2 string
	start        int
}

type NodePair struct {
	node1, node2 string
}

// sorting interface by contact start time
type ByStart []Contact

func (a ByStart) Len() int           { return len(a) }
func (a ByStart) Swap(i, j int)      { a[i], a[j] = a[j], a[i] }
func (a ByStart) Less(i, j int) bool { return a[i].start < a[j].start }
