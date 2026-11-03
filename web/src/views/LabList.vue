<script setup>
import { reactive, ref, onMounted } from 'vue'
import request from '@/utils/request'

const list = ref([])
const loading = ref(true)
const query = reactive({ keyword: '', capacity_min: 0 })   // capacity_min=0 时后端自动忽略该条件

async function load() {
  loading.value = true
  try {
    list.value = await request.get('/labs', { params: query })
  } finally { loading.value = false }
}
onMounted(load)
</script>

<template>
  <div>
    <el-input v-model="query.keyword" placeholder="名称/位置/描述" style="width: 200px" clearable @keyup.enter="load" />
    <el-input-number v-model="query.capacity_min" :min="0" style="width: 140px; margin: 0 8px" />
    <el-button type="primary" @click="load">查询</el-button>

    <el-row :gutter="16" v-loading="loading" style="margin-top: 16px">
      <el-col :span="8" v-for="lab in list" :key="lab.id" style="margin-bottom: 16px">
        <el-card shadow="hover" style="cursor: pointer" @click="$router.push(`/labs/${lab.id}`)">
          <h3>{{ lab.name }} <el-tag :type="lab.status === '开放中' ? 'success' : 'warning'">{{ lab.status }}</el-tag></h3>
          <p>{{ lab.location }} · 容纳 {{ lab.capacity }} 人</p>
        </el-card>
      </el-col>
    </el-row>
    <el-empty v-if="!loading && !list.length" description="没有匹配的实验室" />
  </div>
</template>