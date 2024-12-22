<template>
<router-view :key="$route.fullPath"></router-view>
<ul>
  <li v-for="mall in malls" style="margin: 1rem;">
  <!-- <router-link :to="{ path: `/malls/${mall.id}`}">{{ mall.name }}</router-link> -->
    <button v-if="Number($route.params.mallId) === mall.id" class="button_blue" style="background-color: var(--secondary-color);" @click="goToMall(mall)">{{ mall.name }}</button>
    <button v-else class="button_blue" @click="goToMall(mall)">{{ mall.name }}</button>
  </li>
</ul>
</template>

<script>
import { useRoute } from 'vue-router';
export default {
  data() {
    return {
      malls: [],
      route: null
    }
  },
  async mounted() {
    const user = JSON.parse(localStorage.getItem('user'));
    const token = localStorage.getItem('token');

    const $this = this;
    await this.$axios.get('/api/malls', {
      headers: { 'Authorization': `Bearer ${token}` }
    }).then(function(response) {
      $this.malls = response.data;
    }).catch(function(error) {
      const msg = error?.response?.data.error || error;
      alert(msg);
      localStorage.removeItem('user');
      localStorage.removeItem('token');
      $this.$router.push('/');
    });
    this.route = useRoute();
  },
  methods: {
    goToMall(mall) {
      //this.$router.push('/');
      this.$router.push(`/malls/${mall.id}`);
      //this.$forceUpdate();
      //console.log(this.route.path);
    }
  },
}
</script>

<style scoped>
ul {
  list-style: none;
}
</style>