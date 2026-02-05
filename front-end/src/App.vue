<template>
  <div class="container" style="width: 1200px; margin: 50px auto;">
    <h1 style="text-align: center; margin-bottom: 30px;">课程评价分析系统</h1>
    
    <!-- 1. 评价提交区域 -->
    <el-card title="提交课程评价" style="margin-bottom: 20px;">
      <el-form :model="commentForm" label-width="100px" @submit.prevent="submitComment">
        <el-form-item label="课程名称">
          <el-input v-model="commentForm.courseName" placeholder="请输入课程名称"></el-input>
        </el-form-item>
        <el-form-item label="评价内容">
          <el-input
            v-model="commentForm.comment"
            type="textarea"
            :rows="5"
            placeholder="请输入对课程的评价"></el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="submitComment">提交评价</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 2. 统计数据区域 -->
    <el-card title="评价统计分析" style="margin-bottom: 20px;">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-statistic title="总评价数" :value="statistics.total"></el-statistic>
        </el-col>
        <el-col :span="6">
          <el-statistic title="正面评价" :value="statistics.positive" color="#67C23A"></el-statistic>
        </el-col>
        <el-col :span="6">
          <el-statistic title="负面评价" :value="statistics.negative" color="#F56C6C"></el-statistic>
        </el-col>
        <el-col :span="6">
          <el-statistic title="中性评价" :value="statistics.neutral" color="#909399"></el-statistic>
        </el-col>
      </el-row>
      <!-- 简单的可视化图表 -->
      <div id="chart" style="width: 100%; height: 300px; margin-top: 20px;"></div>
    </el-card>

    <!-- 3. 评价列表区域 -->
    <el-card title="课程评价列表">
      <el-table :data="commentList" border style="width: 100%">
        <el-table-column prop="id" label="ID" width="80"></el-table-column>
        <el-table-column prop="course_name" label="课程名称" width="200"></el-table-column>
        <el-table-column prop="comment" label="评价内容" min-width="400"></el-table-column>
        <el-table-column prop="score" label="情感得分" width="120">
          <template #default="scope">
            <el-tag :color="scope.row.score > 0.6 ? 'success' : (scope.row.score < 0.4 ? 'danger' : 'warning')">
              {{ scope.row.score }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="create_time" label="提交时间" width="200"></el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, getCurrentInstance } from 'vue'
import * as echarts from 'echarts'

// 获取全局Axios
const { proxy } = getCurrentInstance()

// 1. 表单数据
const commentForm = ref({
  courseName: '',
  comment: ''
})

// 2. 评价列表数据
const commentList = ref([])

// 3. 统计数据
const statistics = ref({
  total: 0,
  positive: 0,
  negative: 0,
  neutral: 0
})

// 初始化图表
function initChart() {
  const chartDom = document.getElementById('chart')
  const myChart = echarts.init(chartDom)
  const option = {
    title: { text: '评价情感分布' },
    tooltip: { trigger: 'item' },
    series: [
      {
        name: '评价数量',
        type: 'pie',
        radius: ['40%', '70%'],
        data: [
          { value: statistics.value.positive, name: '正面评价' },
          { value: statistics.value.negative, name: '负面评价' },
          { value: statistics.value.neutral, name: '中性评价' }
        ],
        label: {
          show: true,
          formatter: '{b}: {c} ({d}%)'
        }
      }
    ]
  }
  myChart.setOption(option)
  window.addEventListener('resize', () => {
    myChart.resize()
  })
}

// 获取评价列表
async function getCommentList() {
  try {
    const res = await proxy.$axios.get('/comments')
    if (res.data.code === 200) {
      commentList.value = res.data.data
    } else {
      proxy.$message.error(res.data.msg)
    }
  } catch (error) {
    proxy.$message.error('获取评价列表失败')
    console.error(error)
  }
}

// 获取统计数据
async function getStatistics() {
  try {
    const res = await proxy.$axios.get('/statistics')
    if (res.data.code === 200) {
      statistics.value = res.data.data
      initChart() // 获取数据后初始化图表
    } else {
      proxy.$message.error(res.data.msg)
    }
  } catch (error) {
    proxy.$message.error('获取统计数据失败')
    console.error(error)
  }
}

// 提交评价
async function submitComment() {
  if (!commentForm.value.courseName || !commentForm.value.comment) {
    proxy.$message.warning('课程名称和评价内容不能为空')
    return
  }
  try {
    const res = await proxy.$axios.post('/comment', {
      courseName: commentForm.value.courseName,
      comment: commentForm.value.comment
    })
    if (res.data.code === 200) {
      proxy.$message.success('评价提交成功！情感得分：' + res.data.data.score)
      // 清空表单
      commentForm.value.courseName = ''
      commentForm.value.comment = ''
      // 重新加载数据
      getCommentList()
      getStatistics()
    } else {
      proxy.$message.error(res.data.msg)
    }
  } catch (error) {
    proxy.$message.error('提交评价失败')
    console.error(error)
  }
}

// 页面加载时获取数据
onMounted(() => {
  getCommentList()
  getStatistics()
})
</script>

<style scoped>
.container {
  font-family: "Microsoft YaHei", sans-serif;
}
</style>