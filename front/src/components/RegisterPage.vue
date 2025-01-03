<template>
  <nav class="navigation">
    <router-link to="/login">Вход</router-link>
    <span style="color: var(--primary-color);"> | </span>
    <span style="color: var(--primary-color);">Регистрация</span>
  </nav>
  <div class="register-page">
      <h2>Регистрация</h2>
      <form @submit.prevent="register" class="form-group">
        <input v-model="formData.name" type="text" placeholder="Имя" required name="name" autocomplete="name" />
        <input v-model="formData.email" type="email" placeholder="Электронная почта" required name="email" autocomplete="email" />
        <input v-model="formData.password" type="password" placeholder="Пароль" required name="password" />
        <button type="submit">Зарегистрироваться</button>
      </form>
  </div>
</template>
  
<script>
  export default {
    data() {
      return {
        formData: {
          name: "",
          email: "",
          password: "",
        }
      };
    },
    async beforeCreate() {
      document.title = "Регистрация";
    },
    methods: {
      async register() {
        const $this = this;
        this.$axios.post('/api/register-create', this.formData
        ).then(function (response) {
          alert('Регистрация отправлена на рассмотрение');
           $this.$router.push('/');
        }).catch(function (error) {
          console.error(error);
          const msg = error?.response?.data.error || error;
          alert('Ошибка при регистрации\n' + msg);
        })
      }
    }
  };
</script>

<style scoped>
.register-page {
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