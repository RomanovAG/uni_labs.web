<template>
<TopBar></TopBar>
<div>
    settings page for {{ user.name || '/' + user.role + 's/' + user.id }}
</div>
</template>

<script>
import TopBar from '@/components/TopBar.vue';
export default {
  components: {
    TopBar
  },
  data () {
    return {
      user: null
    };
  },
  created() {
    this.user = JSON.parse(localStorage.getItem('user'));
    document.title = (this.user.name || '/' + this.user.role + 's/' + this.user.id) + ' : настройки';
  },
}
</script>