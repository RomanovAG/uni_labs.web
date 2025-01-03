<template>
    <TopBar/>
    <div style="margin: auto; max-width: 70rem;">
    <div style="display: flex;">
      <div>
        <h2 style="margin-top: 1rem;">Управление</h2>
        <MallsList/>
      </div>
      <div style="margin-left: 1rem;">
        <h2 style="margin-top: 1rem;">Заявки</h2>
        <ul style="list-style: none;">
          <li v-for="request in requests" :key="request.id">
            <div class="white_box" style="max-width: 50rem; margin-bottom: 1rem;">
              <p>{{ request.author_name }} - {{ request.author_email }}</p>
              <p>MAC: {{ request.sensor_mac }}</p>
              <div class="button_container">
                <button @click="request_approve(request.sensor_mac, request.author_email)" class="button_green">Одобрить</button>
                <button @click="request_reject(request.sensor_mac, request.author_email)" class="button_red">Отклонить</button>
              </div>
            </div>
          </li>
        </ul>
      </div>
      <div style="margin-left: 1rem;">
        <h2 style="margin-top: 1rem">Заявки на регистрацию</h2>
        <ul style="list-style: none;">
          <li v-for="user in pending_users" :key="user.id">
            <div class="white_box" style="max-width: 50rem; margin-bottom: 1rem;">
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
        pending_users: [],
        requests: []
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

      this.$axios.get(`/api/sensors/requests`, {
        headers: { Authorization: `Bearer ${token}` }
      }).then(function(response) {
        $this.requests = response.data;
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
      },
      async request_approve(mac, email) {
        const user = JSON.parse(localStorage.getItem('user'));
        const token = localStorage.getItem('token');
        const $this = this;
        await this.$axios.post(`/api/sensors/${mac}/request-approve`, {
          headers: { Authorization: `Bearer ${token}` },
          email: email
        }).then(function(response) {
          alert('Одобрено');
          $this.requests = $this.requests.filter(r => !(r.sensor_mac == mac && r.author_email == email));
        }).catch(function(error) {

        });
      },
      async request_reject(mac, email) {
        const user = JSON.parse(localStorage.getItem('user'));
        const token = localStorage.getItem('token');
        const $this = this;
        await this.$axios.post(`/api/sensors/${mac}/request-reject`, {
          headers: { Authorization: `Bearer ${token}` },
          email: email
        }).then(function(response) {
          alert('Отклонено');
          $this.requests = $this.requests.filter(r => !(r.sensor_mac == mac && r.author_email == email));
        }).catch(function(error) {

        });
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