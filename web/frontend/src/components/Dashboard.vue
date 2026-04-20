<template>
    <v-container >
        <v-row>
            <v-col cols="4">
                <!-- Pilih broker -->
                <v-autocomplete
                    v-model="selectedBrokers"
                    :items="allBrokers"
                    label="Select Item"
                    clearable
                    multiple
                    density="compact"
                    variant="outlined"
                    :item-props="(item) => ({                        
                        title: `${item.broker_code} - ${item.broker}`,
                        value: item.broker_code
                    })"
                    :list-props="{ density: 'compact', class: 'pa-0' }"
                    :disabled="autoIndex"
                    @update:model-value="getBrokSum"
                >
                    <template v-slot:prepend-item>
                        <v-list-item
                            title="Select All"
                            @click="toggle2"
                        >
                            <template v-slot:prepend>
                            <v-checkbox-btn
                                :color="selectSomeBrokers ? 'indigo-darken-4' : undefined"
                                :indeterminate="selectSomeBrokers && !selectAllBrokers"
                                :model-value="selectAllBrokers"
                            ></v-checkbox-btn>
                            <v-icon icon='mdi-select-all' size="24" ></v-icon>                     
                            </template>
                        </v-list-item>

                        <v-divider class="mt-2"></v-divider>
                    </template> 
                    <template v-slot:selection="{ item, index }">
                        <v-chip v-if="index < 2" :text="item.broker_code"></v-chip>
                                
                        <span
                            v-if="index === 2"
                            class="text-grey text-body-small align-self-center"
                        >
                            (+{{ selectedBrokers.length - 2 }} others)
                        </span>
                        </template>       

                </v-autocomplete>                                  
            </v-col>
            <v-col cols="4">
                <!-- Pilih emiten -->
                <v-autocomplete
                    v-model="selectedStocks"
                    :items="allStocks"
                    label="Select Item"
                    multiple
                    density="compact"
                    variant="outlined"
                    item-value="stock_symbol"
                    clearable
                    :list-props="{
                        density: 'compact', class: 'pa-0'
                    }"
                    :disabled="autoIndex"
                    :item-props="(item) => ({
                                                
                        title: `${item.stock_symbol} - ${item.stock}`,
                        value: item.stock_symbol
                    })"                    
                    item
                    @update:model-value="getBrokSum"
                >      
                    <template v-slot:prepend-item>
                        <v-list-item
                            title="Select All"
                            @click="toggle"
                        >
                            <template v-slot:prepend>
                            <v-checkbox-btn
                                :color="selectSomeStocks ? 'indigo-darken-4' : undefined"
                                :indeterminate="selectSomeStocks && !selectAllStocks"
                                :model-value="selectAllStocks"
                            ></v-checkbox-btn>
                            <v-icon icon='mdi-select-all' size="24" ></v-icon>                     
                            </template>
                        </v-list-item>

                        <v-divider class="mt-2"></v-divider>
                    </template>                
                    <template #item="{ item, props }">
                        <v-list-item v-bind="props">
                            <template #prepend="{ isSelected }">
                                <v-checkbox-btn :model-value="isSelected" class="mr-2" />
                                <v-avatar
                                    :image="`${imgLink}${item.stock_symbol}.png`"
                                    size="24" 
                                    color="grey">
                                </v-avatar>
                            </template>
                        </v-list-item>
                    </template>                                  
                    <template v-slot:selection="{ item, index }">
                        <v-chip v-if="index < 2" :text="item.stock_symbol"></v-chip>
                                
                        <span
                            v-if="index === 2"
                            class="text-grey text-caption align-self-center"
                        >
                            (+{{ selectedStocks.length - 2 }} others)
                        </span>
                    </template>       

                </v-autocomplete>  
            </v-col>
            <v-col cols=2>
                <v-date-input 
                    label="First Date"
                    density="compact"
                    variant="outlined"
                    v-model="firstDate"
                    autocomplete="False"
                    @update:model-value="getBrokSum"
                >
                </v-date-input>
            </v-col>
            <v-col cols=2>
                <v-date-input 
                    label="Second Date"
                    density="compact"
                    variant="outlined"
                    v-model="secondDate"
                    
                    @update:model-value="getBrokSum"
                >
                </v-date-input>
            </v-col>            
        </v-row>
        <v-row class="ma-0">
            <v-col cols=2>
                <v-checkbox
                    v-model="autoIndex"
                    density="compact"
                    label="Auto Screened"
                    hide-details                    
                >
                </v-checkbox>
              
            </v-col>
            <!-- <v-col>
                <v-switch
                    v-model="redShade"
                    :label="`Switch: ${redShade}`"
                    false-value="Buy Shade"
                    true-value="Sell Shade"
                    hide-details
                    density="compact"
                    @update:model-value="changeShade"
                ></v-switch>  
            </v-col> -->
            <v-col class="d-flex justify-end">
                <span class="d-flex align-center mr-3">
                    Menunjukan data {{ dataFrom }} - {{ dataTo }} dari {{ totalLimit }} broker. Hal {{ currentPage }} dari {{ totalPage }}
                </span>
                <v-btn 
                    size="36" 
                    icon="mdi-arrow-left" 
                    variant="outlined"
                    :disabled="currentPage <= 1 "
                    @click="navigate(false)" 
                    >                    
                </v-btn>
                <v-btn 
                    size="36" 
                    icon="mdi-arrow-right" 
                    variant="outlined"
                    :disabled="currentPage === totalPage"    
                    @click="navigate(true)"            
                ></v-btn>  
            </v-col>
        </v-row>
        <div id="heatmap"></div>
    </v-container>
    
</template>

<script setup lang="ts">
import ApexCharts from 'apexcharts';
import { onMounted, ref, computed } from 'vue';
import { format } from 'date-fns'
import axios from 'axios'

const imgLink = import.meta.env.VITE_IMG_LINK;
const selectedBrokers = ref<string[]>([])
const allBrokers = ref<{ broker: string; broker_code: string }[]>([])

const selectedStocks = ref<string[]>([])
const allStocks = ref<{ stock_symbol: string; stock: string }[]>([])

const firstDate = ref<Date | null>(null)
const secondDate = ref<Date | null>(null)

const autoIndex = ref<boolean>(false)

const currentPage = ref<number>(1)
const totalLimit = ref<number>(0)
const limit = ref<number>(20)

const redShade = ref<string>('Buy Shade')

const dataFrom = computed(() => {
    return ((currentPage.value -1) * limit.value) + 1
})

const dataTo = computed(() => {
    return (currentPage.value * limit.value) 
})

const totalPage = computed(() => {
    return Math.ceil(totalLimit.value / limit.value)
})
    
type HeatmapPoint = {
    x: string
    y: number
}

type HeatmapSeries = {
    name: string
    data: HeatmapPoint[]
}

const series = ref<HeatmapSeries[]>([])
const chart = ref<ApexCharts | null>(null)

const selectAllStocks = computed(() => {
    return selectedStocks.value.length === allStocks.value.length
})
const selectSomeStocks = computed(() => {
    return selectedStocks.value.length > 0
})

const selectAllBrokers = computed(() => {
    return selectedBrokers.value.length === allBrokers.value.length
})
const selectSomeBrokers = computed(() => {
    return selectedBrokers.value.length > 0
})

function navigate(isNext: boolean) {

    var first_date = firstDate.value?.toISOString().split('T')[0]
    var second_date = secondDate.value?.toISOString().split('T')[0]   

    if (isNext) {
        currentPage.value++
    } else {
        currentPage.value--
    }
    axios.post('http://127.0.0.1:8000/broker-summary-screened', {first_date: first_date, second_date: second_date, limit: limit.value, page: currentPage.value}).then((response) => {
        refreshHeatMap(response.data)
        totalLimit.value = response.data.total_limit
    })     
}

function changeShade() {
    var newOption;
    if (redShade.value === 'Buy Shade') {
        newOption = {
            plotOptions: {
                heatmap: {
                    reverseNegativeShade: false                    
                },
                
            }
        }                       
    } else {
        newOption = {
            plotOptions: {
                heatmap: {
                    reverseNegativeShade: true                    
                },
                
            }
        }   
    }
    chart.value?.updateOptions(newOption)       
}

function toggle () {
    if (selectAllStocks.value) {
        selectedStocks.value = []
    } else {
        selectedStocks.value = allStocks.value.map(item => item.stock_symbol)
    }
}

function toggle2 () {
    if (selectAllBrokers.value) {
        selectedBrokers.value = []
    } else {
        selectedBrokers.value = allBrokers.value.map(item => item.broker_code)
    }
}

function formatNumber(n: number) {
  const abs = Math.abs(n);
  if (abs >= 1_000_000_000_000) return (n / 1_000_000_000_000).toFixed(2) + 'T';
  if (abs >= 1_000_000_000) return (n / 1_000_000_000).toFixed(2) + 'B';
  if (abs >= 1_000_000)     return (n / 1_000_000).toFixed(2) + 'M';
  if (abs >= 1_000)         return (n / 1_000).toFixed(2) + 'K';
  return n.toString();
}

const options = ref<ApexCharts.ApexOptions>({
    chart: {
    type: "heatmap"
    },
    dataLabels: {
        style: {
            colors: ["#000000"],
            fontWeight: 50
        },
        formatter: (data) => formatNumber(Number(data))
    },
    xaxis: {
        labels: {
            style: {
                colors: "#ffffff"
            }
        }
    },
    yaxis: {
        labels: {
            style: {
                colors: "#ffffff"
            }
        }
    },    
    series : series.value,
    plotOptions:{
        heatmap: {
            colorScale: {
                ranges: [
                    { from: -Infinity,             to: -500_000_000_000, color: "#d32f2f", name: "Strong Sell" },
                    { from: -500_000_000_000,      to: -200_000_000_000, color: "#ef5350", name: "Moderate Sell" },
                    { from: -200_000_000_000,      to: -50_000_000_000,  color: "#ffcdd2", name: "Mild Sell" },
                    { from: -50_000_000_000,       to: 0,    color: "#fff3e0", name: "Neutral Sell" },
                    { from: 0,                     to: 50_000_000_000,   color: "#f1f8e9", name: "Neutral Buy" },
                    { from: 50_000_000_000,        to: 200_000_000_000,  color: "#a5d6a7", name: "Mild Buy" },
                    { from: 200_000_000_000,       to: 500_000_000_000,  color: "#66bb6a", name: "Moderate Buy" },
                    { from: 500_000_000_000,       to: Infinity, color: "#2e7d32", name: "Strong Buy" },
                ],
            },     
            reverseNegativeShade: true,
            enableShades: true,
            shadeIntensity: 0.32
        }
    },
    tooltip: {
        enabled: false
    }
})

function refreshHeatMap(response: any) {
        var all_value: number[] = []
        response.data.forEach((item:any) => {
            const value = item.data.map((v:any) => v.y)
            all_value = [...all_value, ...value]
        })    
        var min = Math.min(...all_value)
        var max = Math.max(...all_value)                   
        
        const values = all_value
            .filter((v: any) => v !== 0)
            .sort((a: any, b: any) => a - b);

        const n = values.length;
        const pct = (p: number) => values[Math.min(Math.floor(p * n), n - 1)];

        const newRanges = [
            { from: min,        to: pct(0.10),  color: "#f0545b", name: "Strong Sell"},
            { from: pct(0.10),  to: pct(0.25),  color: "#f78388", name: "Moderate Sell" },
            { from: pct(0.25),  to: pct(0.40),  color: "#f5a9ac", name: "Mild Sell" },
            { from: pct(0.40),  to: pct(0.50),  color: "#f5d0d2", name: "Neutral Sell" },
            { from: pct(0.50),  to: pct(0.60),  color: "#f1f8e9", name: "Neutral Buy" },
            { from: pct(0.60),  to: pct(0.75),  color: "#a5d6a7", name: "Mild Buy" },
            { from: pct(0.75),  to: pct(0.90),  color: "#66bb6a", name: "Moderate Buy" },
            { from: pct(0.90),  to: max,        color: "#2e7d32", name: "Strong Buy" },
        ];     

        const newOption = {
            plotOptions: {
                heatmap: {
                    colorScale: {
                        ranges: newRanges
                    }
                }
            }
        }
        
        series.value = response.data    
        chart.value?.updateSeries(response.data)
        chart.value?.updateOptions(newOption)    
}

function getBrokSum() {
    var first_date ='2026-01-01'
    var second_date = '2026-01-01'
    if (firstDate.value && secondDate.value){
        first_date = format(firstDate.value, 'yyyy-MM-dd')
        second_date = format(secondDate.value, 'yyyy-MM-dd')
    }
    // var second_date = secondDate.value?.toISOString().split('T')[0]
    var param = {
        first_date : first_date,
        second_date : second_date, 
        broker_codes : selectedBrokers.value,
        stocks : selectedStocks.value   
    }

    if (!autoIndex.value)  {
        axios.post('http://127.0.0.1:8000/broker-summary', param).then((response) => {
            refreshHeatMap(response)
        })    
    } else {
        axios.post('http://127.0.0.1:8000/broker-summary-screened', {first_date: first_date, second_date: second_date,  limit: limit.value, page: currentPage.value}).then((response) => {
            refreshHeatMap(response.data)
            totalLimit.value = response.data.total_limit
        }) 
        
    }

}

onMounted(() => {
    const chartElement: HTMLElement | null = document.querySelector("#heatmap");
    if (chartElement) {
        chart.value = new ApexCharts(chartElement, options.value);
        chart.value.render();
    }
    
    axios.get('http://127.0.0.1:8000/get-all-brokers').then((response) => {
        allBrokers.value = response.data.map((row: any[]) => ({'broker_code': row[0], 'broker': row[1]}))
    })

    axios.get('http://127.0.0.1:8000/get-all-stocks').then((response) => {
        allStocks.value = response.data.map((row: any[]) => ({'stock_symbol': row[0], 'stock': row[1]}))
    })    

    axios.post('http://127.0.0.1:8000/broker-summary-screened', {first_date: '2026-04-01', second_date: '2026-04-16'}).then((response) => {
        refreshHeatMap(response)
    })    


})
</script>

