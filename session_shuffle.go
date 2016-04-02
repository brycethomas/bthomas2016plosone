// Reimplement session shuffling algorithms in Go.  See the equivalent Python
// script for more comprehensive commenting of how each of the shuffling
// algorithms work.
package main

import (
	"bufio"
	"flag"
	"fmt"
	"math/rand"
	"os"
	"strconv"
	"strings"
	"sort"
)

func main() {
	seed := flag.Int64("s", 1000, "Seed for random shuffling.")
	flag.Parse()
	rand.Seed(*seed)
	pa := flag.Args()
	if len(pa) > 1 {
		fmt.Fprintf(os.Stderr, "Too many positional arguments!")
		os.Exit(1)
	} else if len(pa) < 1 {
		fmt.Fprintf(os.Stderr, "Too few positional arguments!")
		os.Exit(1)
	}
	alg := strings.ToLower(pa[0])

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

	switch alg {
	case "tn":
		sessions = tn(sessions)
	case "ln":
		sessions = ln(sessions)
	case "tl":
		sessions = tl(sessions)
	case "tlln":
		sessions = tlln(sessions)
	case "lntn":
		sessions = lntn(sessions)
	case "_":
		sessions = destroy_all(sessions)
	default:
		fmt.Fprintf(os.Stderr, "Unrecognized shuffle algorithm: %s",
			alg)
		os.Exit(1)
	}

	// Output the shuffled sessions.
	for _, s := range sessions {
		fmt.Println(strings.Join([]string{
			s.node,
			strconv.Itoa(s.start),
			strconv.Itoa(s.end),
			s.location},
			","))
	}
}

func tn(sessions []Session) []Session {
	for i, _ := range sessions {
		j := rand.Intn(i + 1)
		sessions[i].location, sessions[j].location =
			sessions[j].location, sessions[i].location
	}
	return sessions
}

func ln(sessions []Session) []Session {
	for i, _ := range sessions {
		j := rand.Intn(i + 1)
		sessions[i].start, sessions[j].start =
			sessions[j].start, sessions[i].start
		sessions[i].end, sessions[j].end =
			sessions[j].end, sessions[i].end
	}
	return sessions
}

func tl(sessions []Session) []Session {
	for i, _ := range sessions {
		j := rand.Intn(i + 1)
		sessions[i].node, sessions[j].node =
			sessions[j].node, sessions[i].node
	}
	return sessions
}

func tlln(sessions []Session) []Session {
	// group durations by location.
	loc_durs := make(map[string][]Duration)
	for _, s := range sessions {
		_, ok := loc_durs[s.location]
		if !ok {
			loc_durs[s.location] = []Duration{}
		}
		loc_durs[s.location] = append(loc_durs[s.location],
			Duration{s.start, s.end})
	}
	// in each group shuffle durations.
	// sort keys first to ensure determinism.
	var keys []string
	for k := range loc_durs {
		keys = append(keys, k)
	}
	sort.Strings(keys)
	for _, k := range keys {
		durs := loc_durs[k]
		for i, _ := range durs {
			j := rand.Intn(i + 1)
			durs[i], durs[j] = durs[j], durs[i]
		}
	}
	// apply shuffled durations to the original sessions.
	for i, _ := range sessions {
		loc := sessions[i].location
		// two-step pop
		new_dur := loc_durs[loc][len(loc_durs[loc])-1]
		loc_durs[loc] = loc_durs[loc][:len(loc_durs[loc])-1]

		sessions[i].start, sessions[i].end = new_dur.start, new_dur.end
	}
	return sessions
}

func lntn(sessions []Session) []Session {
	// group locations by node.
	node_locs := make(map[string][]string)
	for _, s := range sessions {
		_, ok := node_locs[s.node]
		if !ok {
			node_locs[s.node] = []string{}
		}
		node_locs[s.node] = append(node_locs[s.node], s.location)
	}
	// in each group shuffle locations.
	// sort keys first to ensure determinism.
	var keys []string
	for k := range node_locs {
		keys = append(keys, k)
	}
	sort.Strings(keys)
	for _, k := range keys {
		locs := node_locs[k]
		for i, _ := range locs {
			j := rand.Intn(i + 1)
			locs[i], locs[j] = locs[j], locs[i]
		}
	}
	// for _, locs := range node_locs {
	// 	for i, _ := range locs {
	// 		j := rand.Intn(i + 1)
	// 		locs[i], locs[j] = locs[j], locs[i]
	// 	}
	// }
	// apply shuffled locations to the original sessions.
	for i, _ := range sessions {
		node := sessions[i].node
		// two-step pop
		new_loc := node_locs[node][len(node_locs[node])-1]
		node_locs[node] = node_locs[node][:len(node_locs[node])-1]

		sessions[i].location = new_loc
	}
	return sessions
}

func destroy_all(sessions []Session) []Session {
	for i, _ := range sessions {
		j := rand.Intn(i + 1)
		sessions[i].node, sessions[j].node =
			sessions[j].node, sessions[i].node
	}
	for i, _ := range sessions {
		j := rand.Intn(i + 1)
		sessions[i].location, sessions[j].location =
			sessions[j].location, sessions[i].location
	}
	return sessions
}

type Session struct {
	node       string
	start, end int
	location   string
}

type Duration struct {
	start, end int
}
