import Vue from 'vue'
import Router from 'vue-router'
import sc from '@/pages/SC'
import pynet from '@/components/py_net'
import display from '@/components/display'

Vue.use(Router)

export default new Router({
  routes: [
    {
    path: '/',
    name: 'index',
    component: sc,
    children:[
      {
        path:'/net',
        component:pynet,
        meta:{
          keepAlive:true  //true是保存缓存，false是不保存
        },
      },
      {
        path:'/display',
        name:'display',
        meta:{
          keepAlive:false  //true是保存缓存，false是不保存
        },
        component:display
      }
    ]
  },

]
})
