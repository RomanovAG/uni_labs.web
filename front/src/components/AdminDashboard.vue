<template>
    <TopBar/>
    <div style="padding: 1rem; display: flex; margin: auto; max-width: 70rem;">
    <MallsList/>
      <div>
        <h2 style="margin-top: 1rem">Заявки на регистрацию</h2>
        <ul>
          <li v-for="user in pending_users" :key="user.id">
            <div class="white_box" style="margin: auto; max-width: 50rem; margin-bottom: 1rem;">
              {{ user.name }} - {{ user.email }} ({{ user.role }})
              <div class="button_container">
                <button @click="approve(user)" class="button_green">Одобрить</button>
                <button @click="reject(user)" class="button_red">Отклонить</button>
              </div>
            </div>
          </li>
        </ul>
      </div>
      
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
        pending_users: []
      };
    },
    async created() {
      const user = JSON.parse(localStorage.getItem('user'));
      const token = localStorage.getItem('token')
      if (!user || !token) this.$router.push('/');

      document.title = user.name || useRoute().path;

      const $this = this;
      let $admin_data;
      this.$axios.get(`/api/admins/${user.id}/data`, {
        headers: { Authorization: `Bearer ${token}` }
      }).then(function(response) {
        $admin_data = response;
      }).catch(function(error) {
        const msg = error?.response?.data.error || error;
        alert(msg);
        localStorage.removeItem('user');
        localStorage.removeItem('token');
        $this.$router.push('/');
      });

      this.$axios.get(`/api/pending-users`, {
        headers: { Authorization: `Bearer ${token}` }
      }).then(function(response) {
        $this.pending_users = response.data;
      }).catch(function(error) {
        const msg = error?.response?.data.error || error;
        alert(msg);
        localStorage.removeItem('user');
        localStorage.removeItem('token');
        $this.$router.push('/');
      });
    },
    methods: {
      async approve(user_to_approve) {
        try {
          const user = JSON.parse(localStorage.getItem('user'));
          const token = localStorage.getItem('token')
          await this.$axios.post(`/api/register-approve`, {
            headers: { Authorization: `Bearer ${token}` },
            email: user_to_approve.email
          });
          alert(`Клиент ${user_to_approve.name} одобрен`);
          this.pending_users = this.pending_users.filter(u => u.id !== user_to_approve.id);
        } catch (error) {
          console.error(error);
        }
      },
      async reject(user_to_reject) {
        try {
          const user = JSON.parse(localStorage.getItem('user'));
          const token = localStorage.getItem('token')
          await this.$axios.post(`/api/register-reject`, {
            headers: { Authorization: `Bearer ${token}` },
            email: user_to_reject.email
          });
          alert(`Клиент ${user_to_reject.name} отклонён`);
          this.pending_users = this.pending_users.filter(u => u.id !== user_to_reject.id);
        } catch (error) {
          console.error(error);
        }
      }
    }
  };
</script>

<style scoped>
ul {
  list-style: none;
}

.button_container {
  display: flex;
  gap: 0.75rem; /* Spacing between the buttons */
  margin-top: 1rem; /* Adjust spacing from content above */
}
.button_red {
    /* width: 100%; */
    background-color: var(--red-color);
    color: #fff;
    border: none;
    /* border:1px solid white; */
    border-radius: 8px;
    padding: 0.75rem;
    font-size: 1rem;
    cursor: pointer;

    &:hover {
      background-color: var(--red-color-dark);
    }
}
.button_green {
    /* width: 100%; */
    background-color: var(--secondary-color);
    color: #fff;
    border: none;
    border-radius: 8px;
    padding: 0.75rem;
    font-size: 1rem;
    cursor: pointer;

    &:hover {
      background-color: var(--secondary-color-dark);
    }
}
</style>