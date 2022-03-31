<template>
    <div class="Echarts" v-loading="loading">
        <div id="main" style="width: 100%;height:100%;" ></div>
    </div>
</template>

<script>
    

    export default {
        name: 'pynet',
        data() {
            return {
               loading:false,
               time:null
            }
        },
        methods: {
            init(){
                
                
                var chartDom = document.getElementById('main');
                
                var myChart = this.$echarts.init(chartDom);
                var option;
                //myChart.showLoading();
                myChart.hideLoading();
                var param = {
                    "time": this.time
                }
                this.axios.post("/api/pynet",param).then(
                    res => {
                    var json =res.data;
                    myChart.hideLoading();
                    myChart.setOption(
                    (option = {
                        title: {
                            text: 'PyPI Ecosystem Dependencies',
                            top: 'bottom',
                            left: 'right'
                        },
                        tooltip:{},
                        animationDurationUpdate: 1500,
                        animationEasingUpdate: 'quinticInOut',
                        series: [
                        {
                            type: 'graph',
                            layout: 'force',
                            // progressiveThreshold: 700,
                            force: {	//力引导布局相关的配置项
                                repulsion: 700,	//节点之间的斥力因子。
                                edgeLength: 10	//边的两个节点之间的距离，这个距离也会受 repulsion。
                            },
                            edgeSymbol : ['none','arrow'],
                            edgeSymbolSize: [5, 5],
                            label: {                // 关系对象上的标签
                                normal: {
                                    show: true,                 // 是否显示标签
                                    position: "inside",         // 标签位置:'top''left''right''bottom''inside''insideLeft''insideRight''insideTop''insideBottom''insideTopLeft''insideBottomLeft''insideTopRight''insideBottomRight'
                                    textStyle: {                // 文本样式
                                        fontSize: 12
                                    }
                                }
                            },
                            data: json.nodes.map(function (node) {
                            return {
                                // x: node.x
                                // y: node.y,
                                id: node.id,
                                name: node.label,
                                value:node.value,
                                symbolSize: 60*(node.norm),
                                label:node.label,
                                itemStyle: {
                                color: node.color
                                
                                }
                            };
                            }),
                            edges: json.edges.map(function (edge) {
                            return {
                                source: edge.sourceID,
                                target: edge.targetID
                            };
                            }),
                            emphasis: {
                                focus: 'adjacency',
                                // label: {
                                //     position: 'right',
                                //     show: true,
                                //     textStyle:{
                                //         fontSize:16
                                //     }
                                // }
                            },
                            roam: true,
                            lineStyle: {
                                width: 0.8,
                                curveness: 0.3,
                                opacity: 0.7
                            }
                        }
                        ]
                    }),
                    true
                    );
                    this.loading=false;
                    }
                ).catch(res => {
                    console.log(res)
                });
                option && myChart.setOption(option);
            } 
        },
        mounted(){
            this.loading=false;
            this.init();
            this.loading=false;
        },
    }
</script>

<style scoped>
    
</style>