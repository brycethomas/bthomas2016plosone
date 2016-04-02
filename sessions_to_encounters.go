// Note this script should produce the same encounter set as the Python version
// for a given set of input sessions, but may not emit them in the same order.
// I believe this is being caused by Python and Go using different sorting
// algorithms meaning the session list can have more than one valid sorting
// leading to more than one valid encounter list ordering.

package main

import (
	"fmt"
	"bufio"
	"strings"
	"strconv"
	"sort"
	"os"
)

func main() {
	// read sessions from stdin
	sessions := []Session{}	
	scanner := bufio.NewScanner(os.Stdin)
	for scanner.Scan() {
		fields := strings.Split(strings.TrimSpace(scanner.Text()), ",")
		node := fields[0]
		start, _ := strconv.Atoi(fields[1])
		end, _ := strconv.Atoi(fields[2])
		location := fields[3]
		sessions = append(sessions, Session{node, start, end, location})
	}

	sort.Sort(ByStart(sessions))
	// key -> location, value -> session list
	cand_encs := make(map[string][]Session)
	contacts := []Contact{}
	imaginary_contact_count := 0
	for _, s := range sessions {
		loc := s.location
		_, ok := cand_encs[loc]
		if !ok {
			cand_encs[loc] = []Session{}
		} else {
			// only sessions with end > this sess start remain
			// candidates.  
			ind := 0
			for _, x := range cand_encs[loc] {
				if x.end > s.start {
					cand_encs[loc][ind] = x
					ind++
				}
			}
			cand_encs[loc] = cand_encs[loc][:ind]
		}
		/* sessions with end < this sess start already filtered.  Any
		/* remaining sessions in cand_encs[loc] are for same loc and
		/* started prior to or at same time as this session by virtue of
		/* sessions being sorted by start time.  Therefore all remianing
		/* sessions in cand_encs[loc] started before this session
		/* started and ended after this session started, implying an
		/* encounter. */
		for _, s2 := range cand_encs[loc] {
			if s.node == s2.node {
				// Can happen under e.g. shuffled sessions.
				imaginary_contact_count++
				continue
			}
			var enc_start, enc_end int
			if s.start > s2.start { 
				enc_start = s.start 
			} else { 
				enc_start = s2.start 
			}
			if s.end < s2.end { 
				enc_end = s.end 
			} else { 
				enc_end = s2.end 
			}
			contacts = append(contacts, Contact{s.node, s2.node,
				enc_start, enc_end, loc})
		}
		cand_encs[loc] = append(cand_encs[loc], s)
	}
	
	// write encounters to stdout
	for _, c := range contacts {
		fmt.Println(strings.Join([]string{
			c.node1,
			c.node2,
			strconv.Itoa(c.start),
			strconv.Itoa(c.end),
			c.location},
			","))
	}
	//fmt.Fprintf(os.Stderr, "Number of imaginary contacts: %d\n", 
	//	imaginary_contact_count)
}

type Session struct {
	node string
	start, end int
	location string
}

type Contact struct {
	node1, node2 string
	start, end int
	location string
}

// sorting interface by session start time.
type ByStart []Session

func (a ByStart) Len() int { return len(a) }
func (a ByStart) Swap(i, j int) { a[i], a[j] = a[j], a[i] }
func (a ByStart) Less(i, j int) bool { return a[i].start < a[j].start }
