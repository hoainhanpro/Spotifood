import type { PageLoad } from './$types';

export const load = (async () => {
  return {
    title: 'Đăng nhập',
    description: 'Đăng nhập vào hệ thống Spotifood'
  };
}) satisfies PageLoad; 