<template>
  <div class="request-form">
    <h2>Оставить запрос</h2>
    
    <!-- Выпадающий список для выбора темы запроса -->
    <div class="form-group">
      <!-- <label for="topic">Тема запроса:</label> -->
      <select v-model="selectedTopic" id="topic">
        <option value="" disabled>Выберите тему</option>
        <option v-for="topic in topics" :key="topic.value" :value="topic.value">
          {{ topic.label }}
        </option>
      </select>
    </div>

    <div class="form-group" v-if="selectedTopic">
      <!-- Поля для темы "Запрос на выделение датчиков" -->
      <div v-if="selectedTopic === 'sensors'">
        <div class="form-group">
        <select v-model="selectedStore" id="store">
        <option value="" disabled>Выберите магазин</option>
        <option v-for="store in stores" :key="store.id">
          {{ store.storeName }}
        </option>
        </select>
        </div>
        <label for="quantity">Количество датчиков:</label>
        <input type="number" v-model="requestDetails.quantity" id="quantity" min="1" max="1000" placeholder="Введите количество" />
      </div>

      <div v-if="selectedTopic === 'maintenance'">
        <div class="form-group">
        <select v-model="selectedStore" id="store">
        <option value="" disabled>Выберите магазин</option>
        <option v-for="store in stores" :key="store.id">
          {{ store.storeName }}
        </option>
        </select>
        </div>
        <label for="maintenanceDetails">Описание проблемы:</label>
        <textarea v-model="requestDetails.description" id="maintenanceDetails" placeholder="Опишите проблему"></textarea>
      </div>

      <!-- Поля для другой темы, например, "Общие вопросы" -->
      <div v-if="selectedTopic === 'general'">
        <label for="generalQuestion">Ваш вопрос:</label>
        <textarea v-model="requestDetails.generalQuestion" id="generalQuestion" placeholder="Введите ваш вопрос"></textarea>
      </div>
    </div>

    <!-- Кнопка отправки -->
    <button @click="submitRequest" :disabled="!isFormValid || quantity === ''" class="button_blue">Отправить запрос</button>
  </div>
</template>

<script>
export default {
  data() {
    return {
      topics: [
        { label: 'Запрос на выделение датчиков', value: 'sensors' },
        { label: 'Запрос на обслуживание', value: 'maintenance' },
        { label: 'Общие вопросы', value: 'general' }
      ],
      selectedTopic: '',
      stores: [],
      selectedStore: '',
      requestDetails: {
        quantity: '',
        description: '',
        generalQuestion: ''
      }
    };
  },
  async mounted() {
    const user = JSON.parse(localStorage.getItem('user'));
    const token = localStorage.getItem('token');
    const response = await this.$axios.get(`/api/clients/${user.id}/data`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    this.stores = response.data.stores;
  },
  computed: {
    isFormValid() {
      if (this.selectedTopic === 'sensors') {
        if (this.selectedStore === '') {
          return false;
        }
        return (
          this.requestDetails.quantity >= 1 && 
          this.requestDetails.quantity <= 1000
        );
      } else if (this.selectedTopic === 'maintenance') {
        if (this.selectedStore === '') {
          return false;
        }
        return this.requestDetails.description !== '';
      } else if (this.selectedTopic === 'general') {
        return this.requestDetails.generalQuestion !== '';
      }
      return false;
    }
  },
  methods: {
    async submitRequest() {
      let requestData = {};

      if (this.selectedTopic === 'sensors') {
        requestData = {
          topic: 'Запрос на выделение датчиков',
          store: this.selectedStore,
          quantity: this.requestDetails.quantity
        };
      } else if (this.selectedTopic === 'maintenance') {
        requestData = {
          topic: 'Запрос на обслуживание',
          store: this.selectedStore,
          description: this.requestDetails.description
        };
      } else if (this.selectedTopic === 'general') {
        requestData = {
          topic: 'Общие вопросы',
          question: this.requestDetails.generalQuestion
        };
      }

      console.log('Отправляем данные:', requestData);
      try {
        const token = localStorage.getItem('token');
        const response = await this.$axios.post('/api/request-create', {
            headers: { Authorization: `Bearer ${token}` },
            r: requestData
      });
      } catch (error) {
        let msg = error.response?.data.error;
        if (!msg) {
          msg = error;
        }
        alert(msg);
      }

      this.resetForm();
    },
    resetForm() {
      this.selectedTopic = '';
      this.requestDetails = {
        quantity: '',
        description: '',
        generalQuestion: ''
      };
    }
  }
};
</script>

<style scoped>

label {
  display: block;
  margin-bottom: 0.5rem;
}

input, select, textarea {
      width: 100%;
      margin-bottom: 1rem;
      padding: 0.75rem;
      border: 1px solid #ddd;
      border-radius: 8px;
      font-size: 1rem;
      max-width: 50rem;
      min-width: 10rem;
      min-height: 3rem;
    }

button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}
</style>
