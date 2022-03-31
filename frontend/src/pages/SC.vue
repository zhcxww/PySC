<template>
    <div id="page" class="wrapper">
        <div class="header">
            <button class="logo" @click="logo">PySC</button>
        <!-- <el-menu :default-active="activeIndex" class="el-menu-demo" mode="horizontal" @select="handleSelect">
            <el-menu-item index="1">处理中心</el-menu-item>
            <el-submenu index="2">
                <template slot="title">我的工作台</template>
                <el-menu-item index="2-1">选项1</el-menu-item>
                <el-menu-item index="2-2">选项2</el-menu-item>
                <el-menu-item index="2-3">选项3</el-menu-item>
                <el-submenu index="2-4">
                <template slot="title">选项4</template>
                <el-menu-item index="2-4-1">选项1</el-menu-item>
                <el-menu-item index="2-4-2">选项2</el-menu-item>
                <el-menu-item index="2-4-3">选项3</el-menu-item>
                </el-submenu>
            </el-submenu>
            <el-menu-item index="3" disabled>消息中心</el-menu-item>
            <el-menu-item index="4"><a href="https://www.ele.me" target="_blank">订单管理</a></el-menu-item>
        </el-menu> -->
        </div>
        <div class="search">
        <h2>Python Open Source Software Supply Chain Visualization</h2>
        
        <div id="word-text-area">
            <el-row>
                <el-col :span="21">
                    <el-input  placeholder="Please input package name" v-model="text"></el-input>
                </el-col>
                <el-col :span="3">
                    <el-button type="primary" icon="el-icon-search" @click="onSubmit" round>Search</el-button>
                </el-col>
            </el-row>

            <!-- <div id="word-operation">
                <el-row>
                    <el-button type="primary" @click="onSubmit" round>生成词云</el-button>
                    <el-button type="success" @click="onDownload" round>下载图片</el-button>
                </el-row>
            </div> -->
        </div>
        </div>
        <!-- <div id="img" v-loading="loading" >
                <el-image :src="'data:image/png;base64,'+pic" :fit="fit">
                    <div slot="error" class="image-slot">
                        <i class="el-icon-picture-outline"></i>
                    </div>
                </el-image>
        </div> -->
        <keep-alive>
            <router-view id ='img' ref="child"/>
        </keep-alive>
    </div>
</template>

<script>
    export default {
        name: 'sc',
        data() {
            return {
                text: '',
                pic: "",
                loading: false,
                activeIndex:1
            }
        },
        mounted(){
            this.$router.push('/net')
        },
        methods: {
            handleSelect(key, keyPath){
                console.log(key, keyPath);
            },

            onSubmit() {
                
                var param={"pkg": this.text};
                this.axios.post("/api/ispkg",param).then(
                    res => {
                        var json=res.data;
                        if(json.r == 0){
                            alert("The package does not exist!")
                        }
                        if(json.r==1){
                            if(this.$route.path == "/net"){
                                this.$router.push({
                                name:"display",
                                params:{
                                    pkg:this.text
                                }
                                }).catch(err => {err})
                            }
                            else{
                                this.$refs.child.init(this.text);
                            }

                        }
                    }).catch(res => {
                    console.log(res)
            });
            



            },
            // onDownload() {
            //     const imgUrl = 'data:image/png;base64,' + this.pic
            //     const a = document.createElement('a')
            //     a.href = imgUrl
            //     a.setAttribute('download', 'word-cloud')
            //     a.click()
            // }
            logo(){
                this.$router.push('/net');
                console.log("enter net");
            }
        }
    }
</script>

<style scoped>
    #page{
        height:100%
    }
    #word-text-area {
        margin-left: 20%;
        margin-right: 20%;
    }

    #img {
        margin-left: 10px;
        margin-right:10px ;
        margin-top: 30px;
        width:100%;
        height: 700px
        
    }
    
    .wrapper {
    width: 100%;
    height: 100%;
    /* background: #f0f0f0; */
}
    .header {
    position: relative;
    box-sizing: border-box;
    width: 100%;
    height: 70px;
    font-size: 22px;
    box-shadow: 0 0 1px rgb(0 0 0 / 25%);
    transition: background-color 0.3s ease-in-out;
    }
    .header .logo {
    float: left;
    margin-left: 60px;
    height: 70px;
    width: 160px;
    vertical-align: middle;
    font-family: "Hiragino Sans GB";
    color: #409EFF;
    background: #FFFFFF;
    font-size:25px;
    cursor: pointer;
    border:0
        }
    .search {
        background: #FFFFFF;
    }
</style>