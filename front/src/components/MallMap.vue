<template>
<!-- <router-view :key="$route.fullPath"></router-view> -->
<TopBar/>

<div>
  <div class="canvas-container" @contextmenu.prevent style="display: flex;">
    <div v-if="isAdminComp" class="white_box" style="margin: 1rem; display: block;padding: 1rem;">
      <button @click="saveSensorsData" class="button_blue" style="margin: 0.25rem; min-width: 3rem;">Сохранить</button>
    </div>

    <canvas style=""
      ref="canvas"
      @mousedown="onMouseDown"
      @mouseup="onMouseUp"
      @mousemove="onMouseMove"
      @wheel="onWheel"

      @mousedown.right="onMouseRightClick"

      @click="stopEditingMac"
    ></canvas>

    <div 
      v-if="contextMenuVisible" 
      :style="{ top: `${contextMenuPosition.y - 65}px`, left: `${contextMenuPosition.x}px` }" 
      class="context-menu"
    >
      <div v-if="(contextAction === 'add')">
      <ul >
        <li @click="addSensor">Установить датчик</li>
      </ul>
      </div>
      <div v-else>
      <div v-if="selectedSensor.accessible || isAdminComp">
      <ul >
        <p>Координаты: ({{ selectedSensor.x.toFixed(0) }}, {{ selectedSensor.y.toFixed(0) }})</p>
        <p>MAC:
          <input v-if="isEditingMac && isAdmin" v-model="selectedSensor.mac" @blur="stopEditingMac" />
          <span v-else @click="startEditingMac">{{ selectedSensor.mac || 'No MAC' }}</span>
        </p>
        <p>Состояние: 
          <select v-if="isAdminComp" v-model="selectedSensor.state">
            <option :value=1>Активен</option>
            <option :value=0>Неактивен</option>
          </select>
          <span v-else>{{ selectedSensor.state === 1 ? 'Активен' : 'Неактивен' }}</span>
        </p>
        <li v-if="isAdmin" @click="deleteSensor">Удалить датчик</li>
        <li @click="hideContextMenu">Закрыть меню</li>
      </ul>
      </div>
      <div v-else>
        <button>Запросить</button>
      </div>
      </div>
      
    </div>
    
    <div 
      v-if="tooltipVisible && (hoveredSensor.accessible || isAdminComp)" 
      :style="{ top: `${tooltipPosition.y - 75}px`, left: `${tooltipPosition.x}px` }" 
      class="tooltip"
    >
      <p>Координаты: ({{ hoveredSensor.x.toFixed(0) }}, {{ hoveredSensor.y.toFixed(0) }})</p>
      <p>MAC: {{ hoveredSensor.mac || 'No MAC' }}</p>
      <p>Состояние: {{ hoveredSensor.state === 0 ? 'Неактивен' : 'Активен' }}</p>
    </div>
    <div 
      v-if="tooltipVisible && !hoveredSensor.accessible && !isAdminComp" 
      :style="{ top: `${tooltipPosition.y - 75}px`, left: `${tooltipPosition.x}px` }" 
      class="tooltip"
    >
      <p>Датчик недоступен</p>
    </div>
    
    <div style="display: block; margin-left: 1rem">
      <div class="white_box" style="padding: 1rem;">
        <p style="text-align: center; margin-bottom: 0.1rem;">Этаж</p>
        <ul>
          <li v-for="(image, index) in mall.images" style="list-style: none;">
            <button v-if="mall.images.length - index - 1 === imageIndex()" 
            @click="changeMallFloor(mall.images.length - index - 1)" class="button_blue" style="margin: 0.25rem; min-width: 3rem; background-color: var(--secondary-color);">
            {{
              mall.images.length - index - 1 - mall.undergroundFloorsCount >= 0 ? 
              mall.images.length - index - 1 - mall.undergroundFloorsCount + 1 : 
              mall.images.length - index - 1 - mall.undergroundFloorsCount
            }}
            </button>
            <button v-else 
            @click="changeMallFloor(mall.images.length - index - 1)" class="button_blue" style="margin: 0.25rem; min-width: 3rem;">
            {{
              mall.images.length - index - 1 - mall.undergroundFloorsCount >= 0 ? 
              mall.images.length - index - 1 - mall.undergroundFloorsCount + 1 : 
              mall.images.length - index - 1 - mall.undergroundFloorsCount
            }}
            </button>
          </li>
        </ul>
      </div>

      <div class="white_box" style="margin-top: 1rem; display: block;padding: 1rem;">
        <ul style="list-style: none;">
          <li><button @click="zoom(-100)" class="button_blue" style="margin: 0.25rem; min-width: 3rem;">+</button></li>
          <li><button @click="zoom(100)"  class="button_blue" style="margin: 0.25rem; min-width: 3rem;">-</button></li>
        </ul>
      </div>
    </div>
    <div v-if="isAdminComp" class="white_box" style="margin: 1rem; display: block;padding: 1rem;"> Датчики на этаже
      <ul style="list-style: none; margin: 1rem;">
        <li v-for="(sensor, id) in sensors" >
          <div v-if="sensor.floor === mall.floor">
            <span>{{sensor.mac}}--</span>
            <span> </span>
            <input type="checkbox" :checked="sensor.state === 1" @change="handleCheckboxChange(sensor, $event)"></input>
          </div >
        </li>
      </ul>
    </div>
  </div>
  
  <div style="display: block;">
    <span>Размер датчиков:</span>
    <input type="number" v-model="sensorSize" id="sensorSize" step="1" @change="drawAll" />
  </div>
</div>
  <div>
    scale: {{ this.scale }}; img x: {{ this.offsetX }} y: {{ this.offsetY }};
  </div>
</template>

<script>
import { useRoute } from 'vue-router';
import TopBar from '@/components/TopBar.vue';
import MallsList from '@/components/MallsList.vue';
export default {
  components: {
      TopBar,
      MallsList,
  },
  data() {
    return {
      canvasWidth: 800,        // Ширина Canvas
      canvasHeight: 600,       // Высота Canvas
      offsetX: 0,               // Позиция X изображения
      offsetY: 0,               // Позиция Y изображения
      scale: 1,                // Масштаб изображения
      isPanning: false,       // Флаг для отслеживания перетаскивания
      panStartX: 0,           // Начальная позиция X при перетаскивании
      panStartY: 0,           // Начальная позиция Y при перетаскивании
      isDragging: false,
      dragOffset: { x: 0, y: 0 },

      sensorSize: 15,
      hoveredSensorScale: 1.25,

      contextMenuVisible: false,
      contextAction: 'add',
      contextMenuPosition: { x: 0, y: 0 },

      tooltipVisible: false,
      tooltipPosition: { x: 0, y: 0 },

      mall: {
        id: null,
        name: null,
        floor: 1,
        floorsCount: null,
        undergroundFloorsCount: null,
        images: [],
      },
      
      image: null,
      sensors: [],

      selectedSensor: null,
      hoveredSensor: null,

      isEditingMac: false,
    };
  },
  computed: {
    isAdminComp() {
      const user = JSON.parse(localStorage.getItem('user'));
      return user.role === 'admin';
    }
  },
  async mounted() {
    const route = useRoute();
    this.mall.id = Number(route.params.mallId);
    const user = JSON.parse(localStorage.getItem('user'));
    const token = localStorage.getItem('token');

    const $this = this;
    await this.$axios.get(`/api/malls/${this.mall.id}/data`, {
      headers: { 'Authorization': `Bearer ${token}` }
    }).then(function(response) {
      const mall = response.data.mall;
      $this.mall.id = mall.id;
      $this.mall.name = mall.name;
      $this.mall.floorsCount = mall.floorsCount;
      $this.mall.undergroundFloorsCount = mall.undergroundFloorsCount;

      if (mall.floorsCount === 0) {
        alert('Отсутствеут карта ТЦ');
        $this.$router.push('/');
      }

      $this.sensors = response.data.sensors;
    })
    document.title =  this.mall.name || route.path;

    const canvas = this.$refs.canvas;
    canvas.width = this.canvasWidth;
    canvas.height = this.canvasHeight;
    this.loadImages();
    try {
      this.image.onload = () => {
        this.offsetX = (this.canvasWidth - this.image.width) / 2;
        this.offsetY = (this.canvasHeight - this.image.height) / 2;
        this.drawAll();
      };
    } catch (error) {}
  },
  methods: {
    clamp(num, min, max) {
      return num <= min
        ? min 
        : num >= max 
          ? max 
          : num
    },
    isAdmin() {
      const user = JSON.parse(localStorage.getItem('user'));
      return user.role === 'admin';
    },
    origCoords(x, y) {
      const rect = this.$refs.canvas.getBoundingClientRect();
      return [ (x - rect.left - this.offsetX) / this.scale, (y - rect.top - this.offsetY) / this.scale];
    },
    imageIndex() {
      if (this.mall.floor < 0) {
        return this.mall.floor + this.mall.undergroundFloorsCount;
      }
      return this.mall.floor + this.mall.undergroundFloorsCount - 1;
    },
    async changeMallFloor(index) {
      this.mall.floor = index - this.mall.undergroundFloorsCount >= 0 ? 
                        index - this.mall.undergroundFloorsCount + 1 : 
                        index - this.mall.undergroundFloorsCount;
      this.image = this.mall.images[this.imageIndex()];
      this.drawAll();
    },
    loadImages() {
      try {
        for (let i = -this.mall.undergroundFloorsCount; i < 0; i++) {
          const image = new Image();
          image.src = require(`@/../media/${this.mall.name}/${i}.png`);
          this.mall.images.push(image);
        }
        for (let i = 1; i <= this.mall.floorsCount - this.mall.undergroundFloorsCount; i++) {
          const image = new Image();
          image.src = require(`@/../media/${this.mall.name}/${i}.png`);
          this.mall.images.push(image);
        }
        this.image = this.mall.images[this.imageIndex()];
      } catch (error) {
        alert(error);
      }
    },
    drawImage() {
      const canvas = this.$refs.canvas;
      const context = canvas.getContext("2d");
      context.save();
      context.translate(this.offsetX, this.offsetY);
      context.scale(this.scale, this.scale);
      try {
        context.drawImage(this.image, 0, 0);
      } catch (error) {}
      context.restore();
    },
    drawSensors() {
      const canvas = this.$refs.canvas;
      const context = canvas.getContext('2d');
      context.save();
      context.translate(this.offsetX, this.offsetY);
      context.scale(this.scale, this.scale);
 
      this.sensors.forEach((sensor) => {
        if (sensor.floor !== this.mall.floor) return;

        const [ x, y ] = [ sensor.x, sensor.y ];
        let [ r, g, b ] = [ 0, 0, 255 ];
        let a = 1;

        if (sensor.accessible === 1 || this.isAdmin()) {
          context.fillStyle = sensor.color || `rgba(${r}, ${g}, ${b}, ${a})`;
        }
        else {
          context.fillStyle = "gray";
          [ r, g, b ] = [ 128, 128, 128 ];
        }

        if (!sensor.state) {
          [ r, g, b ] = [ 128, 0, 0 ];
        }
        context.shadowColor = "rgba(0, 0, 0, 0)";
        context.shadowBlur = 0;

        let sensorSize = this.sensorSize;
        if (sensor === this.hoveredSensor) {
          sensorSize *= this.hoveredSensorScale;
          //context.fillStyle = "rgba(50, 50, 255, 0.65)";
          //[ r, g, b, a ] = [ 50, 50, 255, 0.65 ];
          a = 0.65;
          context.shadowColor = "black";
          context.shadowBlur = 10;
        }
        context.fillStyle = `rgba(${r}, ${g}, ${b}, ${a})`
        
        context.beginPath();
        context.arc(x, y, sensorSize / this.scale, 0, 2 * Math.PI);
        context.fill();

        context.shadowColor = "rgba(0, 0, 0, 0)";
        context.shadowBlur = 0;

        context.lineWidth = 1 / this.scale;
        context.strokeStyle = 'black';
        context.stroke();

        //Обозначение для выделенного датчика
        if (sensor === this.selectedSensor) {
          context.lineWidth = 2 / this.scale;
          context.strokeStyle = "magenta";
          context.stroke();
        }
      });
      context.restore();
    },
    drawAll() {
      this.$refs.canvas.getContext("2d").clearRect(0, 0, this.canvasWidth, this.canvasHeight);
      this.drawImage();
      this.drawSensors();
    },
    async saveSensorsData() {
      const user = JSON.parse(localStorage.getItem('user'));
      const token = localStorage.getItem('token');

      const $this = this;
      await this.$axios.post(`api/malls/${this.mall.id}/save`, {
        headers: { 'Authorization': `Bearer ${token}` },
        sensors: this.sensors
      }).then(function(response) {

      }).catch(function(error) {

      });
    },
    onMouseDown(event) {
      this.contextMenuVisible = false;

      const [ x, y ] = this.origCoords(event.clientX, event.clientY);

      const sensor = this.sensors.find(sensor => Math.hypot(sensor.x - x, sensor.y - y) <= this.sensorSize * (this.hoveredSensor ? this.hoveredSensorScale : 1) / this.scale);

      if (sensor && sensor.floor === this.mall.floor) {
        const user = JSON.parse(localStorage.getItem('user'));
        this.selectedSensor = sensor;
        this.isDragging = event.button === 0 && user.role === 'admin';
        this.dragOffset.x = x - this.selectedSensor.x;
        this.dragOffset.y = y - this.selectedSensor.y;
      } else {
        this.selectedSensor = null;
        this.isPanning = event.button === 0;
        this.panStartX = event.clientX - this.offsetX;
        this.panStartY = event.clientY - this.offsetY;
      }
      this.drawAll();
    },
    onMouseUp() {
      this.isPanning = false;
      this.isDragging = false;
    },
    onMouseMove(event) {
      const [ x, y ] = this.origCoords(event.clientX, event.clientY);

      if (this.isDragging && this.selectedSensor) {
        this.selectedSensor.x = x - this.dragOffset.x;
        this.selectedSensor.y = y - this.dragOffset.y;
        this.drawAll();
      } else if (this.isPanning) {
        this.offsetX = event.clientX - this.panStartX;
        this.offsetY = event.clientY - this.panStartY;

        this.offsetX = this.clamp(this.offsetX, -this.image.width * this.scale, this.canvasWidth);
        this.offsetY = this.clamp(this.offsetY, -this.image.height * this.scale, this.canvasHeight);
        this.drawAll();
      }
      
      if (!this.contextMenuVisible) {
        // Проверяем, наведен ли курсор на датчик для отображения информации
        const sensor = this.sensors.find(sensor => Math.hypot(sensor.x - x, sensor.y - y) <= this.sensorSize * (this.hoveredSensor ? this.hoveredSensorScale : 1) / this.scale);
        
        if (sensor && sensor.floor === this.mall.floor) {
          this.hoveredSensor = sensor;
          this.tooltipPosition = { x: event.clientX + this.sensorSize, y: event.clientY + this.sensorSize };
          this.tooltipVisible = true;
          this.drawAll();
        } else {
          this.tooltipVisible = false;
          this.hoveredSensor = null;
          this.drawAll();
        }
      }
    },
    onWheel(event) {
      const canvas = this.$refs.canvas;
      const rect = canvas.getBoundingClientRect();
      const mouseX = event.clientX - rect.left;
      const mouseY = event.clientY - rect.top;
      const scaleAmount = event.deltaY * -0.001 * this.scale; // Скорость масштабирования
      const newScale = Math.min(Math.max(0.15, this.scale + scaleAmount), 5);

      this.offsetX = (this.offsetX - mouseX) * (newScale / this.scale) + mouseX;
      this.offsetY = (this.offsetY - mouseY) * (newScale / this.scale) + mouseY;

      this.scale = newScale;

      this.offsetX = this.clamp(this.offsetX, -this.image.width * this.scale, this.canvasWidth);
      this.offsetY = this.clamp(this.offsetY, -this.image.height * this.scale, this.canvasHeight);
      
      this.drawAll();
    },
    onMouseRightClick(event) {
      event.preventDefault();
      const user = JSON.parse(localStorage.getItem('user'));
      //if (user.role !== 'admin') return;

      const rect = this.$refs.canvas.getBoundingClientRect();

      this.contextMenuPosition = { x: event.clientX, y: event.clientY };
      this.contextAction = this.selectedSensor ? "settings" : "add";
      this.contextMenuVisible = true;
      this.hideTooltip();
    },
    hideContextMenu() {
      this.contextMenuVisible = false;
    },
    hideTooltip() {
      this.tooltipVisible = false;
    },
    zoom(deltaY) {
      const scaleAmount = deltaY * -0.001 * this.scale;
      const newScale = Math.min(Math.max(0.15, this.scale + scaleAmount), 5);

      const mouseX = this.$refs.canvas.width / 2;
      const mouseY = this.$refs.canvas.height / 2;
      this.offsetX = (this.offsetX - mouseX) * (newScale / this.scale) + mouseX;
      this.offsetY = (this.offsetY - mouseY) * (newScale / this.scale) + mouseY;

      this.scale = newScale;
      this.drawAll();
    },
    addSensor() {
      const [ x, y ] = this.origCoords(this.contextMenuPosition.x, this.contextMenuPosition.y);

      this.sensors.push({
        x,
        y,
        floor: this.mall.floor,
        mac: '192.168.0.1',
        state: 1,
        accessible: 1,
        color: "blue"
      });
      this.selectedSensor = this.sensors[this.sensors.length - 1];
      this.drawAll();
      this.hideContextMenu();
    },
    deleteSensor() {
      const sensorIndex = this.sensors.findIndex(
        sensor => sensor === this.selectedSensor
      );
      if (sensorIndex >= 0) {
        this.sensors.splice(sensorIndex, 1);
        this.drawAll();
      }
      this.selectedSensor = null;
      this.hideContextMenu();
    },
    startEditingMac() {
      this.isEditingMac = true;
    },
    stopEditingMac() {
      this.isEditingMac = false;
    },
    handleCheckboxChange(sensor, event) {
      sensor.state = event.target.checked ? 1 : 0;
      this.drawAll();
      console.log(`Sensor ${sensor.mac} state changed to: ${sensor.state}`);
    }
  }
};
</script>

<style scoped>
.canvas-container {
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
}

canvas {
  border: 1px solid #ccc;
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  cursor: grab;
}
canvas:active {
  cursor: grabbing;
}

.context-menu {
  position: absolute;
  background-color: white;
  border: 1px solid #ddd;
  box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.2);
  padding: 5px;
  z-index: this.sensorSize;
  border-radius: 8px;
}

.context-menu ul {
  list-style: none;
  margin: 0;
  padding: 0;
}

.context-menu li {
  padding: 5px 10px;
  cursor: pointer;
  border-radius: 8px;
}

.context-menu li:hover {
  background-color: #f0f0f0;
}

.tooltip {
  position: absolute;
  background-color: rgba(50, 50, 50, 0.85);
  color: white;
  padding: 8px;
  border-radius: 8px;
  font-size: 0.9em;
  pointer-events: none;
  z-index: 20;
}
</style>