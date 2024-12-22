<template>
  <nav class="navigation">
        <!-- <router-link to="/login">Вход</router-link> -->
    <span style="color: var(--primary-color);">Вход</span>
    <span style="color: var(--primary-color);"> | </span>
    <router-link to="/register">Регистрация</router-link>
  </nav>
  <div class="login-page">
      <h2>Вход</h2>
      <form @submit.prevent="login" class="form-group">
        <input v-model="email" type="email" placeholder="Электронная почта" required name="email" autocomplete="email" />
        <input v-model="password" type="password" placeholder="Пароль" required name="password" />
        <!-- <div class="center"> -->
        <button type="submit">Войти</button>
        <!-- </div> -->
      </form>
  </div>
</template>
  
<script>
  export default {
    data() {
      return {
        email: "",
        password: ""
      };
    },
    async beforeCreate() {
      document.title = "Вход";
    },
    methods: {
      async login() {
        const $this = this;
        this.$axios.post('/api/login', {
          email: this.email,
          password: this.password
        }).then(function (response) {
          const user = response.data.user;
          const token = response.data.token;
          console.log(user.role);
          localStorage.setItem('user', JSON.stringify(user));
          localStorage.setItem('token', token);

          if (user.role === 'admin') {
            $this.$router.push(`/${user.role}s/${user.id}`)
          } else {
            $this.$router.push(`/${user.role}s/profile`)
          }
        }).catch(function (error) {
          console.error(error);
          const msg = error?.response?.data.error || error;
          alert('Ошибка при входе\n' + msg);
        });
      }
    }
  };
</script>

<style>
.login-page {
  max-width: 25rem;
  margin: auto;
  padding: 2rem;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);

  h2 {
    margin-bottom: 1rem;
    text-align: center;
    color: var(--primary-color);
  }

  button {
    width: 100%;
    background-color: var(--primary-color);
    color: #fff;
    border: none;
    border-radius: 8px;
    padding: 0.75rem;
    font-size: 1rem;
    cursor: pointer;

    &:hover {
      background-color: #2980b9;
    }
  }
}
</style>