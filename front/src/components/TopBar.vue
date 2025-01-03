<template>
  <div class="top-bar">
    <div style="margin: auto; max-width: 70rem;">
      <div style="display: flex;">
        <router-link to="/home" class="home-link" title="Домашняя страница">
          {{ user.name }} ({{ user.role }}) 
        </router-link>
        <router-link :to="'/' + user.role + 's/profile/settings'" class="settings-link" style="margin-right: 1em;">Настройки</router-link>
        <button @click="logout" class="button_red" style="padding: 0; height: 2rem; width: 4rem" title="Выйти из аккаунта">Выйти</button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data () {
    return {
      user: null
    };
  },
  async created() {
    const user = JSON.parse(localStorage.getItem('user'));
    this.user = user;
  },
  methods: {
    logout () {
      localStorage.removeItem('user');
      localStorage.removeItem('token');
      this.$router.push('/');
    }
  }
}
</script>

<style scoped>
.top-bar {
  width: 100%;
  margin-top: 0;
  height: 4rem;
  background-color: var(--primary-color);
  padding: 1rem;
  border-radius: 0 0 8px 8px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}
.settings-link {
  white-space: nowrap;
  padding:0.35rem;
  margin: auto;
  color: #fff;
}
.home-link {
  white-space: nowrap;
  padding:0.35rem;
  margin: auto; 
  margin-left: 0; 
  color: #fff;
  border: 1px solid var(--primary-color-dark);
  border-radius: 8px;
  /* box-shadow: -2px 4px 0.0em rgba(0, 0, 0, 0.25), inset -2px 4px 0.15em rgba(255, 255, 255, 0.0); */
}
</style>