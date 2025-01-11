<template>
<TopBar/>
<div>
  <div class="canvas-container" @contextmenu.prevent style="display: flex;">
    <div v-if="isAdminComp" class="white_box" style="margin: 1rem; display: block; padding: 1rem;">
      <button @click="saveSensorsData" class="button_blue" style="margin: 0.25rem; min-width: 3rem;" title="Сохранить состояние и расположение датчиков">Сохранить</button>
    </div>

    <canvas style="margin-top: 1rem;"
      ref="canvas"
      @mousedown="onMouseDown"
      @mouseup="onMouseUp"
      @mousemove="onMouseMove"
      @wheel.prevent="onWheel"

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
              <input style="font-family: 'Consolas'" v-if="isEditingMac && isAdminComp" v-model="selectedSensor.mac" @blur="stopEditingMac" />
              <span  v-else @click="startEditingMac">{{ selectedSensor.mac || 'No MAC' }}</span>
            </p>
            <p>Состояние: 
              <select v-if="isAdminComp" v-model="selectedSensor.state" @click="drawAll" title="Переключить состояние датчика">
                <option :value=1>Активен</option>
                <option :value=0>Неактивен</option>
              </select>
              <span v-else>{{ selectedSensor.state === 1 ? 'Активен' : 'Неактивен' }}</span>
            </p>
            <li v-if="isAdminComp" @click="deleteSensor">Удалить датчик</li>
            <li @click="hideContextMenu">Закрыть меню</li>
          </ul>
        </div>
        <div v-else>
          <div v-if="selectedSensor.requestCreated">Заявка на рассмотрении</div>
          <button v-else @click="createRequest">Запросить</button>
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
        <ul style="margin-top: 0.5rem;">
          <li v-for="(image, index) in mall.images" style="list-style: none;">
            <button v-if="mall.images.length - index - 1 === imageIndex()" 
            @click="changeMallFloor(mall.images.length - index - 1)" class="button_blue" style="margin: 0.25rem; min-width: 3rem; background-color: var(--secondary-color);"
            :title="
                    mall.images.length - index - 1 - mall.undergroundFloorsCount >= 0 ? 
                    mall.images.length - index - 1 - mall.undergroundFloorsCount + 1 : 
                    mall.images.length - index - 1 - mall.undergroundFloorsCount">
            {{
              mall.images.length - index - 1 - mall.undergroundFloorsCount >= 0 ? 
              mall.images.length - index - 1 - mall.undergroundFloorsCount + 1 : 
              mall.images.length - index - 1 - mall.undergroundFloorsCount
            }}
            </button>
            <button v-else 
            @click="changeMallFloor(mall.images.length - index - 1)" class="button_blue" style="margin: 0.25rem; min-width: 3rem;"
            :title="
                    mall.images.length - index - 1 - mall.undergroundFloorsCount >= 0 ? 
                    mall.images.length - index - 1 - mall.undergroundFloorsCount + 1 : 
                    mall.images.length - index - 1 - mall.undergroundFloorsCount">
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
          <li><button @click="zoom(-100)" class="button_blue" style="margin: 0.25rem; min-width: 3rem;" title="Приблизить">+</button></li>
          <li><button @click="zoom(100)"  class="button_blue" style="margin: 0.25rem; min-width: 3rem;" title="Отдалить  ">-</button></li>
        </ul>
      </div>
    </div>
    <div v-if="isAdminComp" class="white_box" style="margin: 1rem; display: block;padding: 1rem;"> Датчики на этаже
      <ul style="list-style: none; margin: 1rem;">
        <li v-for="(sensor, id) in sensors" >
          <div v-if="sensor.floor === mall.floor">
            <span style="font-family: 'Consolas'">{{sensor.mac}}</span>
            <input style="margin-left: 1rem;" type="checkbox" :checked="sensor.state === 1" 
            @change="handleCheckboxChange(sensor, $event)" title="Переключить состояние датчика"></input>
          </div >
        </li>
      </ul>
    </div>
  </div>
  <div style="margin-top: 1rem;">
    <div style="margin: auto; max-width: 75%; text-align: center;">
      <div style="margin: auto; display: flex; max-height: 7rem;">
        <div class="white_box" style="flex: 25%; text-align: left;">
          <span>Точность:</span>
          <input type="number" style="margin-left: 1rem;" v-model="precision" id="precision" step="1" min="1" max="3" @change="drawAll"/>
          <div></div>
          <span>В реальном времени:</span>
          <input type="checkbox" :checked="realTime === true" v-model="realTime" style="margin-left: 1rem;" @change="updateData">
          </input>
          <div></div>
          <span>Кол-во отображаемых устройств: </span>
          <span>{{ devicesNum }}</span>
        </div>
        <div class="white_box" style="flex: 85%; margin-left: 1rem;">
          <input type="range" style="margin-left: 1rem; min-width: 75%;"
                v-model="selectedTimestampIndex" 
                :min="0" 
                :max="transformedData.length - 1" 
                @input="updateSelectedTimestamp" />
          <div style="margin-top: 1rem; " v-if="currentData">
            <p style="text-align: center;">Выбранная временная метка: {{ currentData.timestamp }}</p>
          </div>
        </div>
      </div>
    </div>
    <!-- <select v-if="currentData && isAdminComp">
      <option>
        <p>Данные:</p>
        <pre>{{ currentData.devices }}</pre>
      </option>
    </select> -->
    <div v-if="currentData && isAdminComp">
      <p>Данные:</p>
        <pre>{{ currentData.devices }}</pre>
      </div>
  </div>
  <!-- <div style="display: block;">
    <span>Размер датчиков:</span>
    <input type="number" style="" v-model="sensorSize" id="sensorSize" step="1" @change="drawAll" />
  </div> -->
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
      offsetX: 0,
      offsetY: 0,
      scale: 1,
      isPanning: false,
      panStartX: 0,
      panStartY: 0,
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
      transformedData: [],
      selectedTimestampIndex: 0,
      precision: 1,
      realTime: false,
      devicesNum: 0,

      taskId: null,
    };
  },
  computed: {
    isAdminComp() {
      const user = JSON.parse(localStorage.getItem('user'));
      return user.role === 'admin';
    },
    currentData() {
      return this.transformedData[this.selectedTimestampIndex];
    },
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
    }).catch(function(error) {
      console.error(error);
      const msg = error?.response?.data.error || error;
      alert(error);
    });
    this.getDevices();
    this.startTask();
    document.title =  this.mall.name || route.path;

    this.$nextTick(() => {
      this.setCanvasSize();
    });
    window.addEventListener('resize', this.setCanvasSize);
    this.loadImages();

    const canvas = this.$refs.canvas;
    try {
      this.image.onload = () => {
        this.offsetX = (canvas.width - this.image.width) / 2;
        this.offsetY = (canvas.height - this.image.height) / 2;
        this.drawAll();
      };
    } catch (error) {}
  },
  beforeDestroy() {
    window.removeEventListener('resize', this.setCanvasSize);
    clearInterval(this.taskId);
  },
  beforeRouteLeave (to, from, next) {
    clearInterval(this.taskId);
    next();
  },
  methods: {
    async updateData() {
      await this.getDevices();
      this.selectedTimestampIndex = this.transformedData.length - 1;
      this.drawAll();
    },
    startTask() {
      this.taskId = setInterval(() => {
        if (this.realTime !== true) return;
        //console.log('task');
        //return;
        this.getDevices();
        this.selectedTimestampIndex = this.transformedData.length - 1;
        this.drawAll();
      }, 120 * 1000);
    },
    endTask() {
      clearInterval(this.taskId);
    },
    updateSelectedTimestamp() {
      this.drawAll();
    },
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
    async setCanvasSize() {
      const canvas = this.$refs.canvas;
      try {
        canvas.width = window.innerWidth*0.6;
        canvas.height = window.innerHeight*0.7125;
        this.drawAll();
      } catch (error) {}
    },
    async getDevices() {
      const user = JSON.parse(localStorage.getItem('user'));
      const token = localStorage.getItem('token');
      const $this = this;
      await this.$axios.get(`/api/malls/${this.mall.id}/devices`, {
        headers: { 'Authorization': `Bearer ${token}` }
      }).then(function(response) {
        // console.log(response.data);
        $this.transformedData = response.data;
      });
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
    async drawImage() {
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
    async drawSensors() {
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
    drawSmoothPentagon(x, y, radius, smoothness, context) {
      const angle = (2 * Math.PI) / 5;
      context.beginPath();
      for (let i = 0; i < 5; i++) {
        const x1 = x + radius * Math.cos(i * angle);
        const y1 = y + radius * Math.sin(i * angle);
        const x2 = x + radius * Math.cos((i + 1) * angle);
        const y2 = y + radius * Math.sin((i + 1) * angle);
        
        if (i === 0) {
          context.moveTo(x1, y1);
        } else {
          const cpX1 = x + (x1 + x2) / 2;
          const cpY1 = y + (y1 + y2) / 2;
          context.arcTo(x1, y1, cpX1, cpY1, smoothness);
        }
      }
      context.closePath();
      context.fillStyle = 'lightblue';
      context.fill();
      context.lineWidth = 1 / this.scale;
      context.strokeStyle = 'black';
      context.stroke();
    },
    async drawDevices() {
      const canvas = this.$refs.canvas;
      const context = canvas.getContext('2d');
      context.save();
      context.translate(this.offsetX, this.offsetY);
      context.scale(this.scale, this.scale);

      this.devicesNum = 0;
      this.currentData?.devices.forEach((device) => {
        let [ x, y ] = [ 0, 0 ];
        let [ r, g, b ] = [ 255, 128, 0 ];
        let a = 1;
        let sensorSize = this.sensorSize;
        context.fillStyle = `rgba(${r}, ${g}, ${b}, ${a})`;
        
        let floor = 0;
        let coeff = 0;
        let active = 0;
        device.sensors.forEach(sensor => {
          const found_sensor = this.sensors.find(s => s.mac == sensor.mac);
          if (!found_sensor) return;
          if (!found_sensor.accessible && !this.isAdmin()) return;
          floor += found_sensor.floor * sensor.normalized_rssi;
          x += found_sensor.x * sensor.normalized_rssi;
          y += found_sensor.y * sensor.normalized_rssi;
          coeff += sensor.normalized_rssi;
          active += 1;
        });
        floor /= coeff;
        x /= coeff;
        y /= coeff;

        if (this.precision > active) return;
        if (floor !== this.mall.floor) return;
        //this.drawSmoothPentagon(x, y, sensorSize * 1.25 / this.scale, 5 / this.scale, context);
        context.beginPath();
        context.arc(x, y, sensorSize / 2 / this.scale, 0, 2 * Math.PI);
        context.fill();
        context.lineWidth = 1 / this.scale;
        context.strokeStyle = 'black';
        context.stroke();
        this.devicesNum++;
      });
      context.restore();
    },
    async drawAll() {
      this.$refs.canvas.getContext("2d").clearRect(0, 0, this.$refs.canvas.width, this.$refs.canvas.height);
      this.drawImage();
      this.drawSensors();
      this.drawDevices();
    },
    async saveSensorsData() {
      const user = JSON.parse(localStorage.getItem('user'));
      const token = localStorage.getItem('token');

      const $this = this;
      await this.$axios.post(`api/malls/${this.mall.id}/save`, {
        headers: { 'Authorization': `Bearer ${token}` },
        sensors: this.sensors
      }).then(function(response) {
        alert('Сохранено');
      }).catch(function(error) {
        console.error(error);
        const msg = error?.response?.data.error || error;
        alert(error);
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
      const canvas = this.$refs.canvas;
      if (this.isDragging && this.selectedSensor) {
        this.selectedSensor.x = x - this.dragOffset.x;
        this.selectedSensor.y = y - this.dragOffset.y;
        this.drawAll();
      } else if (this.isPanning) {
        this.offsetX = event.clientX - this.panStartX;
        this.offsetY = event.clientY - this.panStartY;

        this.offsetX = this.clamp(this.offsetX, -this.image.width * this.scale, canvas.width);
        this.offsetY = this.clamp(this.offsetY, -this.image.height * this.scale, canvas.height);
        this.drawAll();
      }
      
      if (!this.contextMenuVisible) {
        // Проверяем, наведен ли курсор на датчик
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

      this.offsetX = this.clamp(this.offsetX, -this.image.width * this.scale, canvas.width);
      this.offsetY = this.clamp(this.offsetY, -this.image.height * this.scale, canvas.height);
      
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
        mac: '00:00:00:00:00:00',
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
    },
    async createRequest() {
      const user = JSON.parse(localStorage.getItem('user'));
      const token = localStorage.getItem('token');
      const $this = this;
      await this.$axios.post(`api/sensors/${this.selectedSensor.mac}/request-create`, {
        headers: { 'Authorization': `Bearer ${token}` }
      }).then(function(response) {
        $this.selectedSensor.requestCreated = 1;
      }).catch(function(error) {
        console.error(error);
        const msg = error?.response?.data.error || error;
        alert(error);
      });
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
  z-index: 1rem;
  /* z-index: this.sensorSize; */
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