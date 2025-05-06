<script lang="ts">
  import { onMount } from 'svelte';
  
  interface UserData {
    role?: string;
    [key: string]: any;
  }
  
  let userData: UserData | null = null;
  let error: string | null = null;
  
  onMount(() => {
    try {
      const storedUser = localStorage.getItem('user');
      if (storedUser) {
        userData = JSON.parse(storedUser);
        console.log('Thông tin user:', userData);
      } else {
        error = 'Không tìm thấy dữ liệu user trong localStorage';
      }
    } catch (e: unknown) {
      const errorMessage = e instanceof Error ? e.message : 'Lỗi không xác định';
      error = `Lỗi khi parse dữ liệu: ${errorMessage}`;
      console.error(e);
    }
  });
</script>

<div class="container py-5">
  <div class="card bg-dark text-white">
    <div class="card-header">
      <h3>Kiểm tra thông tin User</h3>
    </div>
    <div class="card-body">
      {#if error}
        <div class="alert alert-danger">
          {error}
        </div>
      {:else if userData}
        <h4>Thông tin user data:</h4>
        <pre class="bg-dark-subtle p-3 rounded">{JSON.stringify(userData, null, 2)}</pre>
        
        <div class="mt-4">
          <h5>Thuộc tính role:</h5>
          {#if userData.role !== undefined}
            <div class="alert alert-success">
              <strong>userData.role = {userData.role}</strong>
            </div>
          {:else}
            <div class="alert alert-warning">
              Không tìm thấy thuộc tính role trực tiếp trong userData
            </div>
            
            <h5>Các thuộc tính khác có thể chứa role:</h5>
            <ul>
              {#each Object.keys(userData) as key}
                {#if typeof userData[key] === 'object' && userData[key] !== null}
                  <li>
                    <strong>{key}:</strong> 
                    <pre class="bg-dark-subtle p-2 rounded">{JSON.stringify(userData[key], null, 2)}</pre>
                  </li>
                {/if}
              {/each}
            </ul>
          {/if}
        </div>
      {:else}
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Đang tải...</span>
        </div>
      {/if}
    </div>
  </div>
</div>

<style>
  pre {
    overflow-x: auto;
    white-space: pre-wrap;
    word-wrap: break-word;
  }
</style> 