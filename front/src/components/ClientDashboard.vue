<template>
  <TopBar></TopBar>
  <h2 style="margin-top: 1rem; margin-bottom: 0;">Добро пожаловать, {{ client?.name }}!</h2>
  <div style=" padding: 1rem;">
  <div style="display: flex; margin: auto; max-width: 70rem;">
    <MallsList/>
    <!-- <div class="white_box" style="flex: 5; width: 100%;">
      <p style="margin-bottom: 1rem;">Информация о ваших магазинах:</p>
        <li v-for="mall in stores" :key="mall.id" style="list-style-type: none;">
          <button @click="goToMall(mall)" class="button_blue" style="width: 100%; height: 100%; height: 10rem;">{{ mall?.storeName }}</button>
        </li>
    </div> -->
    <div style="flex: 3; width: 100%; margin-left: 1rem;">
      <RequestForm class="white_box">
      </RequestForm>
    </div>
    </div>
  </div>
</template>
  
<script>
  import TopBar from '@/components/TopBar.vue';
  import MallsList from '@/components/MallsList.vue';
  import RequestForm from '@/components/RequestForm.vue';
  import { useRoute } from 'vue-router';
  export default {
    components: {
      TopBar,
      MallsList,
      RequestForm,
    },
    data() {
      return {
        client: {},
      };
    },
    async updated() {
      document.title = this.client?.name || useRoute().path;
    },
    async beforeMount() {
      const user = JSON.parse(localStorage.getItem('user'));
      const token = localStorage.getItem('token')
      if (!user || !token) this.$router.push('/');

      const $this = this;
      this.$axios.get(`/api/clients/${user.id}/data`, {
        headers: { Authorization: `Bearer ${token}` }
      }).then(function(response) {
        $this.client = response.data;
      }).catch(function(error) {
        const msg = error?.response?.data.error || error;
        alert(msg);
        localStorage.removeItem('user');
        localStorage.removeItem('token');
        $this.$router.push('/');
      });

      
    },
    methods: {
      goToMall(mall) {
        this.$router.push(`/malls/${mall.id}`);
      }
    }
  };
</script>

<style scoped>
</style>