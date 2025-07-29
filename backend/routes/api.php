<?php

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Route;
use App\Http\Controllers\CalculatorController;

Route::get('/calc/{slug}', [CalculatorController::class, 'show']);
Route::post('/calc/{slug}', [CalculatorController::class, 'calculate']);
