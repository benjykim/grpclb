package main

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
	"strconv"
	"strings"

	"github.com/tidwall/gjson"
)

// HealthCheckInfo {"Node":"peer0.org1.example.com", "Status":"healthy"}
type HealthCheckInfo struct {
	Node   string `json:"Node"`
	Status string `json:"Status"`
}

func getPrometheusInfo() string {
	url := "http://localhost:9090/api/v1/query"
	param := "?query=sum(rate(container_last_seen[5m]))by(container_label_com_docker_compose_service)<2"
	req, err := http.NewRequest("POST", url+param, nil)
	req.Header.Set("Content-Type", "application/json")

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		panic(err)
	}
	defer resp.Body.Close()

	body, _ := ioutil.ReadAll(resp.Body)

	return string(body)
}

func setNodeStatus(value string) string {
	v, _ := strconv.ParseFloat(strings.TrimSpace(value), 64)
	if float64(v) < 0.99 {
		return "unhealthy"
	}
	return "healthy"
}

func healthCheck(promInfo string) []string {
	arr := []string{}
	value := gjson.Get(promInfo, "data.result")

	value.ForEach(func(key, value gjson.Result) bool {
		tmp := value.String()
		k := gjson.Get(tmp, "metric.container_label_com_docker_compose_service")
		v := gjson.Get(tmp, "value.1")

		node := k.String()
		nodeStatus := setNodeStatus(v.String())
		healthCheckInfo := &HealthCheckInfo{Node: node, Status: nodeStatus}
		res, _ := json.Marshal(healthCheckInfo)
		arr = append(arr, string(res))
		return true
	})

	return arr
}

func printSlice(s []string) {
	fmt.Printf("%v\n", s)
}

func main() {
	promInfo := getPrometheusInfo()
	json := healthCheck(promInfo)
	printSlice(json)
}
