import { test, expect } from './fixtures';

test.describe('Foxx Mart login', () => {
	test('show a focused cart-free login experience', async ({ page }) => {
		await page.goto('account/login/');

		await expect(page.getByRole('heading', { name: 'Sign in to Foxx Mart' })).toBeVisible();
  		await expect(page.getByRole('textbox', { name: 'Email address' })).toBeVisible();
  		await expect(page.getByRole('textbox', { name: 'Password' })).toBeVisible();
		await expect(page.getByRole('link', { name: 'Forgot Password?'})).toBeVisible();
		await expect(page.getByRole('button', { name: 'Sign in' })).toBeVisible();

		await expect(page.getByText('Quick Cart')).toHaveCount(0);
		await expect(page.getByTitle('Cart')).toHaveCount(0);


	});

	test('rejects an invalid password', async ({ page }) => {
		await page.goto('account/login/');
  		await page.getByRole('textbox', { name: 'Email address' }).fill('mufudzi@foxxmart.com');
  		await page.getByRole('textbox', { name: 'Password' }).fill('sadas');
		await page.getByRole('button', { name: 'Sign in' }).click();

  		await expect(page.getByText('Invalid login')).toBeVisible();

	});


	test('signs in and takes the shopper to the mall', async ({ page }) => {
		await page.goto('account/login/');
		await page.getByRole('textbox', { name: 'Email address' }).fill(process.env.E2E_EMAIL!);
		await page.getByRole('textbox', { name: 'Password' }).fill(process.env.E2E_PASSWORD!);
		await page.getByRole('button', { name: 'Sign in' }).click();

		await expect(page).toHaveURL(/\/mall\//);
	});

	test('starts the Google sign-in hand off', async ({page}) => {
		await page.goto('/account/login/');
		const google = page.getByRole('link', { name: 'Continue with Google' });
		await expect(google).toHaveAttribute('href', '/accounts/google/login/')
	});

	test('has a password-recovery route', async ({ loginPage }) => {
		await loginPage.getByRole('link', { name: 'Forgot Password?' }).click();
		await expect(loginPage).toHaveURL(/\/reset_password\//);
	});
	test('send password reset link', async ({ loginPage }) => {
		await loginPage.getByRole('link', { name: 'Forgot Password?' }).click();
		await expect(loginPage).toHaveURL(/\/reset_password\//);
		await loginPage.getByRole('textbox', { name: 'Email' }).fill(process.env.E2E_EMAIL!);
		await expect(loginPage).toHaveURL(/\/reset_password\//);
	})

	test('test registration', async ({ page }) => {
		const timestamp = Date.now();
		const email = `testuser_${timestamp}@foxxmart.com`;
  		await page.goto('account/register/');
  		await expect(page.getByRole('heading', { name: 'Create your account' })).toBeVisible();
		await page.getByRole('textbox', { name: 'Full name' }).fill('test User');
		await page.getByRole('textbox', { name: 'Full name' }).fill('Test User');
		await page.getByRole('textbox', { name: 'Email address' }).fill(email);
		await page.getByLabel('Password', { exact: true }).fill(process.env.E2E_PASSWORD!);
		await page.getByRole('textbox', { name: 'Confirm password', exact: true }).fill(process.env.E2E_PASSWORD!);
		await page.getByRole('button', { name: 'Create account' }).click();
		await expect(page.getByText('FOXX MART / 01 3rd AxisAdditive manufacturing')).toBeVisible();
	});

	test('test registration failure on same email address', async ({ page }) => {
		const timestamp = Date.now();
		const email = `testuser_${timestamp}@foxxmart.com`;
  		await page.goto('http://localhost:8000/account/register/');
  		await expect(page.getByRole('heading', { name: 'Create your account' })).toBeVisible();
		await page.getByRole('textbox', { name: 'Full name' }).fill('test User');
		await page.getByRole('textbox', { name: 'Full name' }).fill('Test User');
		await page.getByRole('textbox', { name: 'Email address' }).fill(email);
		await page.getByLabel('Password', { exact: true }).fill(process.env.E2E_PASSWORD!);
		await page.getByRole('textbox', { name: 'Confirm password' , exact: true }).fill(process.env.E2E_PASSWORD!);
		await page.getByRole('button', { name: 'Create account' }).click();
		await expect(page.getByText('FOXX MART / 01 3rd AxisAdditive manufacturing')).toBeVisible();
  		await page.goto('account/logout/');
  		await expect(page.getByRole('button', { name: 'FoxxMart' })).toBeVisible();
  		await page.getByRole('button', { name: 'FoxxMart' }).click();
    	await page.getByRole('link', { name: 'Register' }).click();
    	await expect(page.getByRole('heading', { name: 'Create your account' })).toBeVisible();
		await page.getByRole('textbox', { name: 'Full name' }).fill('test User');
		await page.getByRole('textbox', { name: 'Full name' }).fill('Test User');
		await page.getByRole('textbox', { name: 'Email address' }).fill(email);
		await page.getByLabel('Password', { exact: true }).fill(process.env.E2E_PASSWORD!);
		await page.getByRole('textbox', { name: 'Confirm password', exact: true }).fill(process.env.E2E_PASSWORD!);
		await page.getByRole('button', { name: 'Create account' }).click();
  		await expect(page.getByText('An account with this email')).toBeVisible();


	});
});

