<template>
  <el-container>
    <el-aside width="400px">
      <el-row>
        <el-col :span="24" style="margin-top: 10px"
          ><strong style="bold;margin:2px 2px;"
            >The Supply Chain Profile</strong
          ></el-col
        >
      </el-row>
      <el-row>
        <el-col :span="6" style="line-height: 40px"> #package: </el-col>
        <el-col :span="6" style="line-height: 40px">
          {{ package_number }}
        </el-col>

        <el-col :span="6" style="line-height: 40px"> #project: </el-col>
        <el-col :span="6" style="line-height: 40px">
          {{ project_number }}
        </el-col>
      </el-row>

      <el-table
        :data="tableData"
        stripe
        height="200"
        border
        style="width: 100%; background: #d3dce6"
      >
        <el-table-column prop="layer" label="Layer" width="200">
        </el-table-column>
        <el-table-column prop="number" label="Package Number" width="200">
        </el-table-column>
      </el-table>
      <div
        id="degree"
        style="width: 100%; height: 350px; margin-top: 20px"
      ></div>
    </el-aside>
    <el-main>
      <el-carousel style="height: 100%" :autoplay="false">
        <el-carousel-item style="height: 100%">
          <div
            style="
              overflow-y: scroll;
              overflow-x: hidden;
              height: 100%;
              width: 100%;
            "
          >
            <div id="tree" style="height: 100%; width: 100%"></div>
          </div>
        </el-carousel-item>

        <el-carousel-item style="height: 100%">
          <div style="height: 100%; width: 100%">
            <div id="evolution" style="height: 100%; width: 100%"></div></div
        ></el-carousel-item>

        <el-carousel-item style="height: 100%">
          <div style="height: 100%; width: 100%">
            <div id="b_d" style="height: 100%; width: 100%"></div></div
        ></el-carousel-item>

        <el-carousel-item style="height: 100%">
          <div style="height: 100%; width: 100%">
            <div id="in_pr" style="height: 100%; width: 100%"></div></div
        ></el-carousel-item>
      </el-carousel>
    </el-main>
  </el-container>
</template>

<script>
export default {
  name: "display",
  data() {
    return {
      pkg: "",
      time: "1585670399",
      tableData: [],
      project_number: 0,
      package_number: 0,
    };
  },
  activated() {
    this.pkg = this.$route.params.pkg;
    this.draw_tree();
  },
  mounted() {
    this.pkg = this.$route.params.pkg;
    this.draw_tree();
  },
  methods: {
    init(text) {
      this.pkg = text;
      this.draw_tree();
    },
    draw_tree() {
      var chartDom = document.getElementById("tree");
      var myChart = this.$echarts.init(chartDom);
      var option;
      myChart.showLoading();
      var container = document.getElementById("tree");
      myChart.on("click", function (params) {
        if (params.componentType === "series") {
          // 点击到了 series 上
          if (!params.value) {
            // 点击的节点有子分支（可点开）
            var elesArr = Array.from(
              new Set(myChart._chartsViews[0]._data._graphicEls)
            );
            var height = 600; // 这里限制最小高
            var currentHeight = 10 * (elesArr.length - 1) || 10; // 每项10px
            var newHeight = Math.max(currentHeight, height);
            container.style.height = newHeight + "px";
            myChart.resize();
          }
        }
      });
      var data_length;
      var degree_data;
      var evolution;
      var between_degree;
      var indegree_pr;
      this.axios
        .post("/api/gettree", { pkg: this.pkg, time: this.time })
        .then((res) => {
          myChart.hideLoading();
          var data = res.data.tree;
          this.project_number = res.data.project_number;
          this.package_number = res.data.package_number;
          this.tableData = res.data.layer;
          degree_data = res.data;
          evolution = res.data.evolution;
          between_degree = res.data.between_degree;
          indegree_pr = res.data.indegree_pagerank;
          // data.children.forEach(function (datum, index) {
          //     index % 100 != 0 && (datum.collapsed = true);
          // });
          data_length = data.children.length;

          myChart.clear();
          myChart.setOption(
            (option = {
              title:{text:"Tree Structure of the Software Supply Chain"},
              tooltip: {
                trigger: "item",
                triggerOn: "mousemove",
              },
              toolbox: {
                feature: {
                  saveAsImage: {},
                },
              },
              series: [
                {
                  type: "tree",
                  data: [data],
                  top: "1%",
                  left: "7%",
                  bottom: "1%",
                  right: "20%",
                  symbolSize: 11,
                  label: {
                    position: "left",
                    verticalAlign: "middle",
                    align: "right",
                    fontSize: 11,
                  },
                  leaves: {
                    label: {
                      position: "right",
                      verticalAlign: "middle",
                      align: "left",
                    },
                  },
                  emphasis: {
                    focus: "descendant",
                  },
                  expandAndCollapse: true,
                  animationDuration: 550,
                  animationDurationUpdate: 750,
                },
              ],
            })
          );

          if (data_length * 15 < 600) {
            container.style.height = 600 + "px";
            myChart.resize();
          } else {
            container.style.height = data_length * 15 + "px";
            myChart.resize();
          }
          // console.log(degree_data);
          this.draw_degree(degree_data);
          this.draw_evolution(evolution);
          this.draw_b_d(between_degree);
          console.log(indegree_pr);
          this.draw_in_pr(indegree_pr);
        })
        .catch((error) => {
          console.log(error);
        });

      option && myChart.setOption(option);
    },
    draw_degree(degree_data) {
      var chartDom = document.getElementById("degree");
      var myChart = this.$echarts.init(chartDom);
      myChart.clear();
      var option;
      var data = degree_data.degree;
      var option = {
        title: {
          text: "In-degree and Out-degree Distribution",
          left: "center",
          top: 0,
        },
        grid: {
          x: 70,
        },
        visualMap: {
          min: 0,
          max: degree_data.max_layer,
          dimension: 2,
          orient: "vertical",
          right: 10,
          top: "center",
          text: ["Layer"],
          calculable: true,
          inRange: {
            color: ["#f2c31a", "#24b7f2"],
          },
        },
        toolbox: {
          feature: {
            saveAsImage: {},
          },
        },
        tooltip: {
          trigger: "item",
          axisPointer: {
            type: "cross",
          },
          formatter: function (datas) {
            return (
              "Package: " +
              datas.data[3] +
              "<br/>Layer: " +
              datas.data[2] +
              "<br/>Out-degree: " +
              datas.data[0] +
              "<br/>In-degree: " +
              datas.data[1]
            );
          },
        },
        xAxis: [
          {
            type: "value",
            name: "Out-degree",
            nameLocation: "center",
            nameGap: 30,
            minInterval: 1,
          },
        ],
        yAxis: [
          {
            type: "log",
            name: "In-degree",
            logBase: 10,
            min: 1,
          },
        ],
        series: [
          {
            name: "price-area",
            type: "scatter",
            symbolSize: 3,
            data: data,
          },
        ],
      };
      myChart.setOption(option);

      option && myChart.setOption(option);
    },
    draw_evolution(evolution_data) {
      console.log(evolution_data);
      var chartDom = document.getElementById("evolution");
      var myChart = this.$echarts.init(chartDom);
      var option;
      myChart.clear();
      option = {
        title: {
          text: "Number of Packages in Different Layers",
        },
        tooltip: {
          trigger: "axis",
          axisPointer: {
            type: "cross",
            label: {
              backgroundColor: "#6a7985",
            },
          },
        },
        legend: {
          data: evolution_data.legend,
        },
        toolbox: {
          feature: {
            saveAsImage: {},
          },
        },
        grid: {
          left: "3%",
          right: "4%",
          bottom: "3%",
          containLabel: true,
        },
        xAxis: [
          {
            type: "category",
            boundaryGap: false,
            name: "Date",
            nameTextStyle: {
              fontSize: 13,
            },
            nameLocation: "center",
            nameGap: 30,
            data: evolution_data.date,
            axisLabel: {
              textStyle: {
                color: "#000",
                fontSize: "12",
                itemSize: "",
              },
            },
          },
        ],
        yAxis: [
          {
            type: "value",
            name: "Number",
            nameTextStyle: {
              fontSize: 13,
            },
            axisLabel: {
              textStyle: {
                color: "#000",
                fontSize: "14",
                itemSize: "",
              },
            },
          },
        ],
        series: evolution_data.series,
      };

      option && myChart.setOption(option);
    },
    draw_b_d(between_degree) {
      var chartDom = document.getElementById("b_d");
      var myChart = this.$echarts.init(chartDom);
      var option;
      myChart.clear();
      option = {
        title: {
          text: "Degree Centrality and Betweenness Centrality of the Packages",
        },
        tooltip: {
          trigger: "item",
          axisPointer: {
            type: "cross",
          },
          formatter: function (datas) {
            return (
              "Package: " +
              datas.data[2] +
              // "<br/>Layer: " +
              // datas.data[2] +
              "<br/>Betweenness Centrality: " +
              datas.data[0] +
              "<br/>Degree Centrality: " +
              datas.data[1]
            );
          },
        },
        toolbox: {
          feature: {
            saveAsImage: {},
          },
        },
        xAxis: [
          {
            type: "log",
            name: " Betweenness Centrality",
            nameTextStyle: {
              fontSize: 13,
            },
            nameLocation: "center",
            nameGap: 30,
            logBase: 10,
            min: 1,
            axisLabel: {
              textStyle: {
                color: "#000",
                fontSize: "14",
                itemSize: "",
              },
            },

            // minInterval: 1,
          },
        ],
        yAxis: [
          {
            type: "log",
            name: "Degree Centrality",
            nameTextStyle: {
              fontSize: 13,
            },
            logBase: 10,
            min: 1,
            axisLabel: {
              textStyle: {
                color: "#000",
                fontSize: "14",
                itemSize: "",
              },
            },
          },
        ],
        series: [
          {
            symbolSize: 5,
            data: between_degree,
            type: "scatter",
            itemStyle: {
              color: "#24b7f2",
            },
          },
        ],
      };

      option && myChart.setOption(option);
    },
    draw_in_pr(indegree_pr) {
      var chartDom = document.getElementById("in_pr");
      var myChart = this.$echarts.init(chartDom);
      var option;
      myChart.clear();
      option = {
        title: {
          text: "In-Degree and Page-Rank of the Packages",
        },
        tooltip: {
          trigger: "item",
          axisPointer: {
            type: "cross",
          },
          formatter: function (datas) {
            return (
              "Package: " +
              datas.data[2] +
              // "<br/>Layer: " +
              // datas.data[2] +
              "<br/>In-Degree: " +
              datas.data[0] +
              "<br/>Page Rank: " +
              datas.data[1]
            );
          },
        },
        toolbox: {
          feature: {
            saveAsImage: {},
          },
        },
        xAxis: [
          {
            type: "log",
            name: " In-Degree",
            nameTextStyle: {
              fontSize: 13,
            },
            nameLocation: "center",
            nameGap: 30,
            logBase: 10,
            min: 1,
            axisLabel: {
              textStyle: {
                color: "#000",
                fontSize: "14",
                itemSize: "",
              },
            },
            // minInterval: 1,
          },
        ],
        yAxis: [
          {
            type: "log",
            name: "Page Rank",
            nameTextStyle: {
              fontSize: 13,
            },
            logBase: 10,
            min: 0.00001,
            axisLabel: {
              textStyle: {
                color: "#000",
                fontSize: "14",
                itemSize: "",
              },
            },
          },
        ],
        series: [
          {
            symbolSize: 5,
            data: indegree_pr,
            type: "scatter",
            itemStyle: {
              color: "#f2c31a",
            },
          },
        ],
      };

      option && myChart.setOption(option);
    },
  },
};
</script>

<style scoped>
.el-aside {
  background-color: #d3dce6;
  color: #333;
  text-align: center;
  /* line-height: 200px; */
}

.el-main {
  background-color: #e9eef3;
  color: #333;
  text-align: center;
  line-height: 160px;
}
.el-row {
  margin-bottom: 20px;
  /* &:last-child {
    margin-bottom: 0;
  } */
}
.el-col {
  border-radius: 4px;
}
.el-carousel /deep/ .el-carousel__container {
  height: 100%;
}
</style>
