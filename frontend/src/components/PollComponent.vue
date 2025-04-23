<template>
  <div class="poll-container">
    <div v-if="error" class="error">
      {{ error }}
    </div>

    <div v-if="poll" class="poll-content">
      <h2 class="question">{{ poll.question }}</h2>
      
      <div class="options" v-if="!hasVoted">
        <div
          v-for="option in poll.options"
          :key="option.id"
          class="option"
          :class="{ selected: selectedOption === option.id }"
          @click="selectOption(option.id)"
        >
          {{ option.text }}
        </div>
        
        <button 
          class="vote-button"
          :disabled="!selectedOption"
          @click="handleSubmitVote"
        >
          提交投票
        </button>
      </div>

      <div v-if="hasVoted || showResults" class="results">
        <h3>投票结果</h3>
        <v-chart class="chart" :option="chartOption" autoresize />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { v4 as uuidv4 } from 'uuid';
import { use } from "echarts/core";
import { CanvasRenderer } from "echarts/renderers";
import { BarChart } from "echarts/charts";
import { GridComponent, TooltipComponent } from "echarts/components";
import VChart from "vue-echarts";
import { getPoll, submitVote, createWebSocket, type Poll } from '../api/poll';

use([CanvasRenderer, BarChart, GridComponent, TooltipComponent]);

const clientId = ref(localStorage.getItem('clientId') || uuidv4());
const poll = ref<Poll | null>(null);
const results = ref<Record<number, number>>({});
const selectedOption = ref<number | null>(null);
const error = ref<string>('');
const hasVoted = ref(false);
const showResults = ref(false);

// 保存客户端ID到localStorage
localStorage.setItem('clientId', clientId.value);

// 图表配置
const chartOption = computed(() => ({
  tooltip: {
    trigger: 'axis',
    axisPointer: {
      type: 'shadow'
    }
  },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '3%',
    containLabel: true
  },
  xAxis: {
    type: 'category',
    data: poll.value?.options.map(opt => opt.text) || [],
    axisLabel: {
      interval: 0,
      rotate: 30
    }
  },
  yAxis: {
    type: 'value'
  },
  series: [
    {
      name: '票数',
      type: 'bar',
      data: poll.value?.options.map(opt => results.value[opt.id] || 0) || [],
      itemStyle: {
        color: '#409EFF'
      }
    }
  ]
}));

// 选择选项
const selectOption = (optionId: number) => {
  selectedOption.value = optionId;
};

// 提交投票
const handleSubmitVote = async () => {
  if (!selectedOption.value) return;
  
  try {
    const response = await submitVote(selectedOption.value, clientId.value);
    results.value = response.results;
    hasVoted.value = true;
    showResults.value = true;
    // 保存投票状态
    localStorage.setItem('voted', 'true');
  } catch (err: any) {
    error.value = err.response?.data?.detail || '投票失败，请稍后重试';
  }
};

// 更新投票结果
const updateResults = (data: any) => {
  if (data.type === 'vote_update') {
    results.value = data.results;
  }
};

// 初始化
const init = async () => {
  try {
    const data = await getPoll();
    poll.value = data.poll;
    results.value = data.results;
    
    // 检查是否已经投票
    const voted = localStorage.getItem('voted') === 'true';
    if (voted) {
      hasVoted.value = true;
      showResults.value = true;
    }
    
    // 建立WebSocket连接
    createWebSocket(updateResults);
  } catch (err) {
    error.value = '加载失败，请刷新页面重试';
  }
};

onMounted(init);
</script>

<style scoped>
.poll-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.error {
  color: #f56c6c;
  margin-bottom: 20px;
  padding: 10px;
  background-color: #fef0f0;
  border-radius: 4px;
}

.question {
  font-size: 24px;
  margin-bottom: 30px;
  color: #303133;
}

.options {
  display: flex;
  flex-direction: column;
  gap: 15px;
  margin-bottom: 30px;
}

.option {
  padding: 15px 20px;
  border: 2px solid #dcdfe6;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
}

.option:hover {
  border-color: #409EFF;
  color: #409EFF;
}

.option.selected {
  border-color: #409EFF;
  background-color: #ecf5ff;
  color: #409EFF;
}

.vote-button {
  margin-top: 20px;
  padding: 12px 20px;
  background-color: #409EFF;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  transition: background-color 0.3s;
}

.vote-button:hover {
  background-color: #66b1ff;
}

.vote-button:disabled {
  background-color: #a0cfff;
  cursor: not-allowed;
}

.results {
  margin-top: 30px;
}

.results h3 {
  margin-bottom: 20px;
  color: #303133;
}

.chart {
  height: 400px;
  width: 100%;
}
</style> 